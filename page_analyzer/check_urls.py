import requests
from flask import flash


def check(url):  # ДОПИСАТЬ ФУНКЦИЮ
    try:
        response = requests.get(url)
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'error')
        return None