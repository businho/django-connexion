def test_settings(settings):
    assert settings.INSTALLED_APPS == ['django_connexion.tests.testapp']


def test_json_spec(client):
    response = client.get('/helloworld/openapi.json')
    content = response.json()
    assert content['info']['title'] == 'Hello World'


def test_yaml_spec(client):
    response = client.get('/helloworld/openapi.yaml')
    assert b'title: Hello World' in response.content


def test_endpoint(client):
    response = client.post('/helloworld/greeting/ze')
    assert b'Hello World' in response.content
    # content = response.json()
    # assert 'Hello World' in content
