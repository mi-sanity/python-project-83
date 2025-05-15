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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=["GET"])
def get_urls():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    repo = UrlsRepository(conn)
    urls = repo.get_all_urls()
    conn.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=["GET"])
def show_url(id):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    repo = UrlsRepository(conn)
    url = repo.get_url_id(id)
    if url is None:
        return render_template('error_page_404.html', url=url)

    url_data, checks = repo.get_url_checks(id)
    conn.close()
    return render_template('url.html', id=id, url=url_data, checks=checks)


@app.route('/urls', methods=['POST'])
def create_url():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    repo = UrlsRepository(conn)
    url_data = request.form.get('url')
    normal_url = setting_format_url(url_data)
    errors = validate(normal_url)

    if errors:
        for message in errors.values():
            flash(message, 'alert-danger')
        return render_template('index.html'), 422

    try:
        url_name = repo.get_url_name(normal_url)
        if url_name:
            flash('Страница уже существует', 'alert-info')
            redirect_url = redirect(
                url_for('show_url', id=url_name['id']),
            )
        else:
            url_id = repo.save_url(normal_url)
            flash('Страница успешно добавлена', 'alert-success')
            redirect_url = redirect(
                url_for('show_url', id=url_id)
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
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    repo = UrlsRepository(conn)
    url = repo.get_url_id(id)

    if url:
        url_name = url['name']
        data = seo_data(url_name)
        if 'error' not in data:
            repo.save_check(id, data)
            flash('Страница успешно проверена', 'alert-success')
        else:
            flash(data['error'], 'alert-danger')
    else:
        flash('URL не найден', 'alert-danger')

    conn.close()
    return redirect(url_for('show_url', id=id))
