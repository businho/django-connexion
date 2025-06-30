# Django Connexion

Uma extensão Django para [Connexion](https://connexion.readthedocs.io/en/latest/index.html) que permite integração perfeita entre Django e especificações OpenAPI 3.x.

### Install
## Características

With poetry:
```sh
poetry add django-connexion
```
- 🚀 Integração nativa com Django e Connexion 3.x
- 📝 Suporte completo para especificações OpenAPI/Swagger
- 🔒 Sistema de autenticação e autorização integrado
- 🧪 Configuração moderna com `pyproject.toml`
- ✅ Código formatado com Black e verificado com Flake8/MyPy
- 📊 Cobertura de testes configurada

## Instalação

With pip:

```bash
pip install django-connexion
```

## Uso Básico

```python
from django_connexion import DjangoApi
from django.urls import path, include

# Criar API a partir da especificação OpenAPI
api = DjangoApi("openapi.yaml")  # ou openapi.json

urlpatterns = [
    path("api/", include(api.urls)),
    path("admin/", admin.site.urls),
]
```

## Exemplo Completo

### 1. Especificação OpenAPI (`openapi.yaml`)

```yaml
openapi: 3.0.0
info:
  title: Minha API
  version: 1.0.0
paths:
  /hello/{name}:
    post:
      summary: Saudação personalizada
      parameters:
        - name: name
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Sucesso
          content:
            text/plain:
              schema:
                type: string
```

### 2. View Django (`views.py`)

```python
from django.http import HttpRequest, HttpResponse

def post_hello(request: HttpRequest, name: str) -> HttpResponse:
    return HttpResponse(f"Olá, {name}!")

doc_api = DjangoApi("openapi.json") # path to openapi file (json or yaml).
```

### 3. Configuração de URLs (`urls.py`)

```python
from django.urls import path, include
from django_connexion import DjangoApi

# ... any code
api = DjangoApi("openapi.yaml")

urlpatterns = [
  path("", doc_api.urls),
  # ... rest of urls
  path('admin/', admin.site.urls),
    path("api/", include(api.urls)),
]
```

## Comandos Disponíveis `make`

```bash
make help          # Mostrar todos os comandos disponíveis
make install       # Instalar dependências de produção
make install-dev   # Instalar dependências de desenvolvimento
make test          # Executar testes
make test-cov      # Executar testes com cobertura
make lint          # Verificar qualidade do código
make format        # Formatar código
make check         # Executar todas as verificações
make build         # Construir pacote
make clean         # Limpar arquivos temporários
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Links

- [Documentação do Connexion](https://connexion.readthedocs.io/)
- [Documentação do Django](https://docs.djangoproject.com/)
- [Especificação OpenAPI](https://swagger.io/specification/)

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
