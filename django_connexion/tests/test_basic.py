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
    assert b'Hello ze' in response.content


def test_get_query_params(client):
    first_names = ['Phoebe', 'Frank Jr. Jr.']
    last_name = 'Buffay'
    expected_text = 'Phoebe Buffay, Frank Jr. Jr. Buffay'

    response = client.get('/helloworld/names/list',
                          {'last_name': last_name, 'first_names': first_names})
    response_text = response.content.decode('utf-8')

    assert response_text == expected_text
