"""
This module defines a Django Connexion API which implements translations between Django and
Connexion requests / responses.
"""
from connexion.apis.abstract import AbstractAPI


class DjangoApi(AbstractAPI):
    """
    Defines an abstract interface for a Swagger API
    """

    def add_openapi_json(self):
        """
        Adds openapi spec to {base_path}/openapi.json
             (or {base_path}/swagger.json for swagger2)
        """

    def add_swagger_ui(self):
        """
        Adds swagger ui to {base_path}/ui/
        """

    def add_auth_on_not_found(self, security, security_definitions):
        """
        Adds a 404 error handler to authenticate and only expose the 404 status if the security validation pass.
        """

    @staticmethod
    def make_security_handler_factory(pass_context_arg_name):
        """ Create SecurityHandlerFactory to create all security check handlers """

    def _add_operation_internal(self, method, path, operation):
        """
        Adds the operation according to the user framework in use.
        It will be used to register the operation on the user framework router.
        """

    @classmethod
    def get_request(self, *args, **kwargs):
        """
        This method converts the user framework request to a ConnexionRequest.
        """

    @classmethod
    def get_response(self, response, mimetype=None, request=None):
        """
        This method converts a handler response to a framework response.
        This method should just retrieve response from handler then call `cls._get_response`.
        It is mainly here to handle AioHttp async handler.
        :param response: A response to cast (tuple, framework response, etc).
        :param mimetype: The response mimetype.
        :type mimetype: Union[None, str]
        :param request: The request associated with this response (the user framework request).
        """

    @classmethod
    def _is_framework_response(cls, response):
        """ Return True if `response` is a framework response class """

    @classmethod
    def _framework_to_connexion_response(cls, response, mimetype):
        """ Cast framework response class to ConnexionResponse used for schema validation """

    @classmethod
    def _connexion_to_framework_response(cls, response, mimetype, extra_context=None):
        """ Cast ConnexionResponse to framework response class """

    @classmethod
    def _build_response(cls, data, mimetype, content_type=None, status_code=None, headers=None, extra_context=None):
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
