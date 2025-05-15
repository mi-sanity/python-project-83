import validators


def validate(url_data):
    errors = {}

    if not url_data:
        errors['name'] = 'Заполните это поле'
        return errors

    if len(url_data) > 255:
        errors['name'] = 'URL превышает 255 символов'
        return errors

    if not validators.url(url_data):
        errors['name'] = 'Некорректный URL'

    return errors
