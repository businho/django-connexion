"""
This module defines a Django Connexion API which implements translations between Django and
Connexion requests / responses.
"""

import json
import logging

from connexion.apis.abstract import AbstractAPI
from connexion.lifecycle import ConnexionRequest, ConnexionResponse
from connexion.utils import yamldumper
from django.http import HttpResponse, JsonResponse
from django.urls import path as django_path
from django.views.decorators.http import require_http_methods

from django_connexion.apis import django_utils
from django_connexion.security.django_security_handler_factory import DjangoSecurityHandlerFactory

logger = logging.getLogger('connexion.apis.django_api')


class DjangoApi(AbstractAPI):
    """
    Defines an abstract interface for a Swagger API
    """
    def __init__(self, *args, name='django_connexion', **kwargs):
        self.name = name
        self._url_patterns = []
        super().__init__(*args, **kwargs)

    def add_openapi_json(self):
        """
        Adds openapi spec to {base_path}/openapi.json
             (or {base_path}/swagger.json for swagger2)
        """
        self._url_patterns.append(
            django_path('openapi.json', self._handlers.get_json_spec)
        )

    def add_openapi_yaml(self):
        """
        Adds spec yaml to {base_path}/swagger.yaml
        or {base_path}/openapi.yaml (for oas3)
        """
        self._url_patterns.append(
            django_path('openapi.yaml', self._handlers.get_yaml_spec)
        )

    def add_swagger_ui(self):
        """
        Adds swagger ui to {base_path}/ui/
        """

    def add_auth_on_not_found(self, security, security_definitions):
        """
        Adds a 404 error handler to authenticate and only expose the 404 status if the security
        validation pass.
        """

    @staticmethod
    def make_security_handler_factory(pass_context_arg_name):
        """ Create SecurityHandlerFactory to create all security check handlers """
        return DjangoSecurityHandlerFactory(pass_context_arg_name)

    def _add_operation_internal(self, method, path, operation):
        """
        Adds the operation according to the user framework in use.
        It will be used to register the operation on the user framework router.
        """
        operation_id = operation.operation_id
        logger.debug('... Adding %s -> %s', method.upper(), operation_id,
                     extra=vars(operation))

        _django_path = django_utils.djangofy_path(path, operation.get_path_parameter_types())
        endpoint_name = django_utils.djangofy_endpoint(operation.operation_id,
                                                       operation.randomize_endpoint)
        function = operation.function
        methods_decorator = require_http_methods([method.upper()])
        decorated_function = methods_decorator(function)

        _path = django_path(_django_path.lstrip('/'), decorated_function, name=endpoint_name)
        self._url_patterns.append(_path)

    @classmethod
    def get_request(self, request, *args, **params):
        """
        This method converts the user framework request to a ConnexionRequest.
        """
        context_dict = {'request': request}
        body = request.body

        connexion_request = ConnexionRequest(
            request.path,
            request.method,
            headers=request.headers,
            form=request.POST,
            query=request.GET,
            body=body,
            json_getter=lambda: request.content_type == 'application/json' and json.loads(body),
            files=request.FILES,
            path_params=params,
            context=context_dict
        )
        logger.debug('Getting data and status code',
                     extra={
                         'data': connexion_request.body,
                         'data_type': type(connexion_request.body),
                         'url': connexion_request.url
                     })
        return connexion_request

    @classmethod
    def get_response(cls, response, mimetype=None, request=None):
        """
        This method converts a handler response to a framework response.
        This method should just retrieve response from handler then call `cls._get_response`.
        It is mainly here to handle AioHttp async handler.
        :param response: A response to cast (tuple, framework response, etc).
        :param mimetype: The response mimetype.
        :type mimetype: Union[None, str]
        :param request: The request associated with this response (the user framework request).
        """
        return cls._get_response(response, mimetype=mimetype)

    @classmethod
    def _is_framework_response(cls, response):
        """ Return True if `response` is a framework response class """
        return django_utils.is_django_response(response)

    @classmethod
    def _framework_to_connexion_response(cls, response, mimetype):
        """ Cast framework response class to ConnexionResponse used for schema validation """
        content_type = response.headers['Content-Type']

        if not mimetype:
            try:
                mimetype, _ = content_type.split(';', 1)
            except ValueError:
                mimetype = content_type

        return ConnexionResponse(
            status_code=response.status_code,
            mimetype=mimetype,
            content_type=content_type,
            headers=response.headers,
            body=response.content,
        )

    @classmethod
    def _connexion_to_framework_response(cls, response, mimetype, extra_context=None):
        """ Cast ConnexionResponse to framework response class """
        content_type = response.content_type
        if not content_type:
            content_type = f'{mimetype or response.mimetype}; charset=utf-8'

        django_response = HttpResponse(
            status=response.status_code,
            content_type=content_type,
            content=response.body,
            headers=response.headers,
        )
        return django_response

    @classmethod
    def _build_response(cls, data, mimetype, content_type=None, status_code=None, headers=None,
                        extra_context=None):
        """
        Create a framework response from the provided arguments.
        :param data: Body data.
        :param content_type: The response mimetype.
        :type content_type: str
        :param content_type: The response status code.
        :type status_code: int
        :param headers: The response status code.
        :type headers: Union[Iterable[Tuple[str, str]], Dict[str, str]]
        :param extra_context: dict of extra details, like url, to include in logs
        :type extra_context: Union[None, dict]
        :return A framework response.
        :rtype Response
        """
        if cls._is_framework_response(data):
            return HttpResponse(data, status_code=status_code, headers=headers)

        data, status_code, serialized_mimetype = cls._prepare_body_and_status_code(
            data=data, mimetype=mimetype, status_code=status_code, extra_context=extra_context)

        mimetype = mimetype or serialized_mimetype
        if content_type is None:
            content_type = 'text/plain'

        if ';' not in content_type:
            content_type += '; charset=utf-8'

        kwargs = {
            'content_type': content_type,
            'headers': headers,
            'status': status_code
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return HttpResponse(data, **kwargs)

    @property
    def urls(self):
        return self._url_patterns, 'django_connexion', self.name

    @property
    def _handlers(self):
        # type: () -> InternalHandlers
        if not hasattr(self, '_internal_handlers'):
            self._internal_handlers = InternalHandlers(
                self.base_path, self.options, self.specification)
        return self._internal_handlers


class InternalHandlers:
    """
    Django handlers for internally registered endpoints.
    """

    def __init__(self, base_path, options, specification):
        self.base_path = base_path
        self.options = options
        self.specification = specification

    def get_json_spec(self, request):
        spec = self._spec_for_prefix(request)
        return JsonResponse(spec)

    def get_yaml_spec(self, request):
        content = yamldumper(self._spec_for_prefix(request))
        return HttpResponse(content, content_type='text/yaml')

    def _spec_for_prefix(self, request):
        """
        Modify base_path in the spec based on incoming url
        This fixes problems with reverse proxies changing the path.
        """
        base_path = '/'
        return self.specification.with_base_path(base_path).raw
