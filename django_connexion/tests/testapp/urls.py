from django.urls import path

from django_connexion.tests.testapp.apis import helloworld_api

urlpatterns = [
    path('helloworld/', helloworld_api.urls),
]
