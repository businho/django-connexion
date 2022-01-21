from django_connexion.locals.context import set_request


class ConnexionMiddleware:
    """Middleware class to store the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_request(request)
        return self.get_response(request)
