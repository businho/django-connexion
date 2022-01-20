from django.http import HttpResponse


def post_greeting(*args, **kwargs) -> str:
    print('DATA', args, kwargs)
    return HttpResponse('ok')
    # return HttpResponse(f'Hello {name}')
