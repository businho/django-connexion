#!/usr/bin/env python3
import datetime
import uuid

from connexion.lifecycle import ConnexionResponse

from django.http import HttpRequest, HttpResponse


def get_bye(name):
    return HttpResponse(text=f'Goodbye {name}')


def django_str_response():
    return 'str response'


def django_non_str_non_json_response():
    return 1234


def django_bytes_response():
    return b'bytes response'


def django_validate_responses():
    return {"validate": True}


def django_post_greeting(name, **kwargs):
    data = {'greeting': f'Hello {name}'}
    return data


def django_echo(**kwargs):
    return django.web.json_response(data=kwargs, status=200)


def django_access_request_context(request_ctx):
    assert request_ctx is not None
    assert isinstance(request_ctx, HttpRequest)
    return None


def django_query_parsing_str(query):
    return {'query': query}


def django_query_parsing_array(query):
    return {'query': query}


def django_query_parsing_array_multi(query):
    return {'query': query}


USERS = [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Nick Carlson"}
]


def django_users_get(*args):
    return django.web.json_response(data=USERS, status=200)


def django_users_post(user):
    if "name" not in user:
        return ConnexionResponse(body={"error": "name is undefined"},
                                 status_code=400,
                                 content_type='application/json')
    user['id'] = len(USERS) + 1
    USERS.append(user)
    return django.web.json_response(data=USERS[-1], status=201)


def django_token_info(token_info):
    return django.web.json_response(data=token_info)


def django_all_auth(token_info):
    return django_token_info(token_info)


def django_async_auth(token_info):
    return django_token_info(token_info)


def django_bearer_auth(token_info):
    return django_token_info(token_info)


def django_async_bearer_auth(token_info):
    return django_token_info(token_info)


def get_datetime():
    return ConnexionResponse(body={'value': datetime.datetime(2000, 1, 2, 3, 4, 5, 6)})


def get_date():
    return ConnexionResponse(body={'value': datetime.date(2000, 1, 2)})


def get_uuid():
    return ConnexionResponse(body={'value': uuid.UUID(hex='e7ff66d0-3ec2-4c4e-bed0-6e4723c24c51')})
