import json

import pytest
from django_connexion.apis.django_api import DjangoApi
from connexion.lifecycle import ConnexionResponse

from django.http import HttpResponse, StreamingHttpResponse


@pytest.fixture(scope='module')
def api(django_api_spec_dir):
    yield DjangoApi(specification=django_api_spec_dir / 'swagger_secure.yaml')


def test_get_response_from_django_response(api):
    django_response = HttpResponse(
        'foo', status=201, headers={'X-header': 'value'}, content_type='text/plain; charset=utf-8')
    response = api.get_response(django_response)
    assert isinstance(response, HttpResponse)
    assert response.status_code == 201
    assert response.content == b'foo'
    assert dict(response.headers) == {
        'Content-Type': 'text/plain; charset=utf-8',
        'X-header': 'value'
    }


def test_get_response_from_django_stream_response(api):
    response = api.get_response(StreamingHttpResponse(status=201, headers={'X-header': 'value'}))
    assert isinstance(response, StreamingHttpResponse)
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/octet-stream'
    assert dict(response.headers) == {'X-header': 'value'}


def test_get_response_from_connexion_response(api):
    connexion_response = ConnexionResponse(
        status_code=201, mimetype='text/plain', body='foo', headers={'X-header': 'value'})
    response = api.get_response(connexion_response)
    assert isinstance(response, HttpResponse)
    assert response.status_code == 201
    assert response.content == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8', 'X-header': 'value'}


def test_get_response_from_string(api):
    response = api.get_response('foo')
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response.content == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8'}


def test_get_response_from_string_tuple(api):
    response = api.get_response(('foo',))
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response.content == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8'}


def test_get_response_from_string_status(api):
    response = api.get_response(('foo', 201))
    assert isinstance(response, HttpResponse)
    assert response.status_code == 201
    assert response.content == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8'}


def test_get_response_from_string_headers(api):
    response = api.get_response(('foo', {'X-header': 'value'}))
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response.content == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8', 'X-header': 'value'}


def test_get_response_from_string_status_headers(api):
    response = api.get_response(('foo', 201, {'X-header': 'value'}))
    assert isinstance(response, HttpResponse)
    assert response.status_code == 201
    assert response.content == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8', 'X-header': 'value'}


def test_get_response_from_tuple_error(api):
    with pytest.raises(TypeError) as e:
        api.get_response((HttpResponse('foo', status=201, headers={'X-header': 'value'}), 200))
    assert str(e.value) == "Cannot return web.StreamResponse in tuple. Only raw data can be returned in tuple."


def test_get_response_from_dict(api):
    response = api.get_response({'foo': 'bar'})
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    # odd, yes. but backwards compatible. see test_response_with_non_str_and_non_json_body in tests/aiohttp/test_aiohttp_simple_api.py
    # TODO: This should be made into JSON when aiohttp and flask serialization can be harmonized.
    assert response.content == b"{'foo': 'bar'}"
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8'}


def test_get_response_from_dict_json(api):
    response = api.get_response({'foo': 'bar'}, mimetype='application/json')
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert json.loads(response.content.decode()) == {"foo": "bar"}
    assert dict(response.headers) == {'Content-Type': 'application/json; charset=utf-8'}


def test_get_response_no_data(api):
    response = api.get_response(None, mimetype='application/json')
    assert isinstance(response, HttpResponse)
    assert response.status_code == 204
    assert response.content is None
    assert dict(response.headers) == {'Content-Type': 'application/json'}


def test_get_response_binary_json(api):
    response = api.get_response(b'{"foo":"bar"}', mimetype='application/json')
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert json.loads(response.content.decode()) == {"foo": "bar"}
    assert dict(response.headers) == {'Content-Type': 'application/json'}


def test_get_response_binary_no_mimetype(api):
    response = api.get_response(b'{"foo":"bar"}')
    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response.content == b'{"foo":"bar"}'
    assert response.headers['Content-Type'] == 'application/octet-stream'
    assert dict(response.headers) == {}


def test_get_connexion_response_from_django_response(api):
    response = api.get_connexion_response(HttpResponse('foo', status=201, content_type='text/plain; charset=utf-8', headers={'X-header': 'value'}))
    assert isinstance(response, ConnexionResponse)
    assert response.status_code == 201
    assert response.body == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8', 'X-header': 'value'}


def test_get_connexion_response_from_connexion_response(api):
    response = api.get_connexion_response(ConnexionResponse(status_code=201, content_type='text/plain', body='foo', headers={'X-header': 'value'}))
    assert isinstance(response, ConnexionResponse)
    assert response.status_code == 201
    assert response.body == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8', 'X-header': 'value'}


def test_get_connexion_response_from_tuple(api):
    response = api.get_connexion_response(('foo', 201, {'X-header': 'value'}))
    assert isinstance(response, ConnexionResponse)
    assert response.status_code == 201
    assert response.body == b'foo'
    assert dict(response.headers) == {'Content-Type': 'text/plain; charset=utf-8', 'X-header': 'value'}


def test_get_connexion_response_from_django_stream_response(api):
    response = api.get_connexion_response(StreamingHttpResponse(status=201, headers={'X-header': 'value'}))
    assert isinstance(response, ConnexionResponse)
    assert response.status_code == 201
    assert response.content == None
    assert dict(response.headers) == {'X-header': 'value'}
