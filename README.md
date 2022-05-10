## Django Connexion

This is a django api for [connexion lib](https://connexion.readthedocs.io/en/latest/index.html).

## Get started

### Install 

With poetry:
```sh
poetry add django-connexion
```

With pip:
```sh
pip install django-connexion
```

### Use

```python
from django_connexion import DjangoApi

doc_api = DjangoApi("openapi.json") # path to openapi file (json or yaml).

# ... any code

urlpatterns = [
  path("", doc_api.urls),
  # ... rest of urls
  path('admin/', admin.site.urls),
]
```
