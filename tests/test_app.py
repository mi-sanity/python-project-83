import pytest

from page_analyzer import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_index(client):
    """Тест для главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello, World!' in response.data