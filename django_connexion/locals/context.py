from contextvars import ContextVar

_request = ContextVar('request', default=None)


def set_request(request):
    """Set the request on the context."""
    _request.set(request)


def get_request():
    """Return the currently set request (if any)."""
    return _request.get()
