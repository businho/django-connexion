from typing import List
from django.http import HttpResponse, HttpRequest


def post_greeting(request: HttpRequest, name: str) -> HttpResponse:
    return HttpResponse(f'Hello {name}')


def list_names(request: HttpRequest, last_name: str, first_names: List[str] = None) -> HttpResponse:
    if first_names is None:
        first_names = ["Pikachu", "Charizard"]
    if isinstance(first_names, str):
        first_names = [first_names]

    return HttpResponse(", ".join([f"{fn} {last_name}" for fn in first_names]))
