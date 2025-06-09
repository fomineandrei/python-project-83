import pytest

from page_analyzer.app import create_app


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
    print(app.path)
    return app.test_cli_runner()


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
