from django.http import HttpResponse


def post_greeting(request, name) -> str:
    return HttpResponse(f'Hello {name}')

def upload_file(request) -> dict:
    return HttpResponse({})
