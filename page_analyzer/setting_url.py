from urllib.parse import urlparse


def setting_format_url(url):
    url_parse = urlparse(url.lower())
    normal_url = f"{url_parse.scheme}://{url_parse.netloc}".rstrip("/")
    return normal_url
