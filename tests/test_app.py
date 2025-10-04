import os
from urllib.parse import urlparse

import pytest

os.environ["TEST"] = 'True'

from page_analyzer.app import create_app
from page_analyzer.http import get_http_response
from page_analyzer.models.db import db_engine
from page_analyzer.models.models import Url, UrlCheck
from tests.test_data.http_test import FakeHttp

db_test = db_engine()


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def connection():
    connect = db_test.get_connection()
    return connect


@pytest.fixture(autouse=True)
def transaction(connection):
    yield
    connection.rollback()


def test_config_1(app):    
    assert app.config['APPLICATION_ROOT'] == '/'


def test_config_2(app):    
    assert app.config['TESTING'] is True


def test_index_status(client):
    response = client.get('/')
    assert response.status_code == 200


def test_index_title(client):
    response = client.get('/')
    title_name = 'Анализатор страниц by Fomine Andrei'
    assert b'<title>' + title_name.encode() + b'</title>' in response.data


def test_index_body(client):
    response = client.get('/')
    h1 = '<h1 class="display-3">Анализатор страниц</h1>'
    assert h1.encode() in response.data


def test_urls_get(client, connection):
    test_url_db = db_test.save_url(connection, "https://for-test-1.com")
    test_url = Url(**test_url_db)
    test_check_data = UrlCheck(url_id=test_url.id, status_code=404)
    test_check_db = db_test.check_save(connection, test_check_data)
    test_check = UrlCheck(**test_check_db)
    response = client.get('/urls')
    test1 = f"""<td>{test_url.id}</td>
          <td><a href="/urls/{test_url.id}">{test_url.name}</a></td>
          <td>{test_check.created_at.date()}</td>
          <td>404</td>"""
    assert test1.encode() in response.data


def test_urls_post_incorrect_url(client):
    response = client.post(
        '/urls', data={'url': 'wrong_url'}, follow_redirects=True)
    redirected_url = response.request.path
    path = urlparse(redirected_url).path
    assert path == '/urls'
    assert len(response.history) == 0
    assert 'Некорректный URL'.encode() in response.data


def test_urls_post_correct_url_new(client, connection):
    response = client.post('/urls',
                           data={'url': 'https://for-test-1.com'},
                           follow_redirects=True)
    redirected_url = response.request.path
    path = urlparse(redirected_url).path
    id = db_test.find_url_by_name(connection, 'https://for-test-1.com').get('id')
    assert path == f'/urls/{id}'
    assert len(response.history) == 2
    assert 'Страница успешно добавлена'.encode() in response.data


def test_urls_post_correct_url_in_db(client, connection):
    url_data = db_test.save_url(connection, 'https://for-test-1.com')
    response = client.post('/urls',
                           data={'url': 'https://for-test-1.com'},
                           follow_redirects=True)
    redirected_url = response.request.path
    path = urlparse(redirected_url).path
    id = url_data.get('id')
    assert path == f'/urls/{id}'
    assert len(response.history) == 1
    assert 'Страница уже существует'.encode() in response.data


def test_url_info(client, connection):
    url_db = db_test.save_url(connection, 'https://for-test-1.com')
    url = Url(**url_db)
    url_check = UrlCheck(url_id=url.id, status_code=200, h1='h1_test',
                         title='title_test', description='description_test')
    check_db = db_test.check_save(connection, url_check)
    check = UrlCheck(**check_db)
    response = client.get(f'/urls/{url.id}')
    test_data = f'''<tr>
          <td scope="row">ID</td>
          <td>{url.id}</td>
        </tr>
        <tr>
          <td scope="row">Имя</td>
          <td>{url.name}</td>
        </tr>
        <tr>
          <td scope="row">Дата создания</td>
          <td>{url.created_at.date()}</td>
        </tr>'''
    assert test_data.encode() in response.data
    test_check_data = f"""<tr>
          <td>{check.id}</td>
          <td>{check.status_code}</td>
          <td>{check.h1}</td>
          <td>{check.title}</td>
          <td>{check.description}</td>
          <td>{check.created_at.date()}</td>
        </tr>"""
    assert test_check_data.encode() in response.data


def test_url_check(connection):
    class UrlTestData:
        def __init__(self):
            self.status_code = 200
            self.h1 = 'h1_test'
            self.title = 'title_test'
            self.description = 'description_test'
    
    url_test = db_test.save_url(connection, 'https://for-test-1.com')
    url_in_db = db_test.find_url_by_id(connection, url_test['id'])
    url = Url(**url_in_db)
    url_test_data = UrlTestData()
    http_response = get_http_response(url_test_data, client=FakeHttp)   
    url_info = UrlCheck(url_id=url.id, **http_response)
    db_test.check_save(connection, url_info)

    checks = db_test.get_url_checks(connection, url_info.url_id)
    check = checks[0]
    assert url_test_data.status_code == check.get('status_code')
    assert url_test_data.h1 == check.get('h1')
    assert url_test_data.title == check.get('title')
    assert url_test_data.description == check.get('description')
