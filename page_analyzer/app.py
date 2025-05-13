import os

import psycopg2
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from psycopg2.extras import DictCursor
from page_analyzer.repository import UrlsRepository
from page_analyzer.seo_analysis import seo_data
from page_analyzer.setting_url import setting_format_url
from page_analyzer.validator import validate

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
repo = UrlsRepository(conn)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=["GET"])
def get_urls():
    urls = repo.get_all_urls()
    conn.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=["GET"])
def show_url(id):
    url = repo.get_url_id(id)
    conn.close()
    if url is None:
        return render_template('error_page_404.html', url=url)
    
    try:
        url_data, checks = repo.get_url_checks(id)
    finally:
        conn.close()
    return render_template('url.html', url=url_data, checks=checks)


@app.route('/urls', methods=['POST'])
def create_url():
    url_data = request.form.get('url')
    normal_url = setting_format_url(url_data)
    errors = validate(normal_url)

    if errors:
        for error in errors:
            flash(error, 'alert-danger')
        return render_template('index.html'), 422

    try:
        url = repo.get_url_name(normal_url)
        if url:
            flash('Страница уже существует', 'alert-info')
            redirect_url = redirect(
                url_for('show_url', url_id=url.get('id')),
            )

        flash('Страница успешно добавлена', 'alert-success')
        redirect_url = redirect(
            url_for('show_url'), url_id=repo.save_url(normal_url)
        )

    except Exception as e:
        conn.rollback()
        flash(
            f'Произошла ошибка при добавлении URL: {e}', 'alert-danger'
        )
        redirect_url = render_template('index.html'), 422

    finally:
        conn.close()
    return redirect_url


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    url = repo.get_url_id(id)

    if url:
        data = seo_data(url)
        if 'error' not in data:
            repo.save_check(id, data)
            flash('Страница успешно проверена', 'alert-success')
        else:
            flash(data['error'], 'alert-danger')
    else:
        flash('URL не найден', 'alert-danger')

    conn.close()
    return redirect(url_for('show_url', id=id))
