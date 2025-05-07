import validators


def validate(url_data):
    errors = {}
    if not url_data.get('name'):
        errors['name'] = 'Заполните это поле'
    if len(url_data.get('name')) > 255:
        errors['name'] = 'URL превышает 255 символов'
    if validators.url(url_data) is not True:
        errors['name'] = 'Некорректный URL'
    return errors
