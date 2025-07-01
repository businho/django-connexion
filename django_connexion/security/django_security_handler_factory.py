"""
Django Security Handler Factory for Connexion 3.x

This module provides security handling compatible with Connexion 3.x architecture.
"""

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("connexion.security.django")


class DjangoSecurityHandlerFactory:
    """
    Security handler factory for Django integration with Connexion 3.x

    This factory creates security handlers that work with Django's authentication
    and authorization system while being compatible with Connexion 3.x middleware.
    """

    def __init__(self, pass_context_arg_name: Optional[str] = None):
        """
        Initialize the security handler factory

        :param pass_context_arg_name: Name of the argument to pass context to handlers
        """
        self.pass_context_arg_name = pass_context_arg_name

    def get_tokeninfo_func(self, token_info_func: Callable) -> Callable:
        """
        Get token info function wrapper for Django

        :param token_info_func: Original token info function
        :return: Wrapped function
        """

        def wrapper(token: str) -> Optional[Dict[str, Any]]:
            try:
                return token_info_func(token)
            except Exception as e:
                logger.error(f"Error in token info function: {e}")
                return None

        return wrapper

    def get_basic_auth_func(self, basic_auth_func: Callable) -> Callable:
        """
        Get basic auth function wrapper for Django

        :param basic_auth_func: Original basic auth function
        :return: Wrapped function
        """

        def wrapper(
            username: str, password: str, required_scopes: Optional[list] = None
        ) -> Optional[Dict[str, Any]]:
            try:
                return basic_auth_func(username, password, required_scopes)
            except Exception as e:
                logger.error(f"Error in basic auth function: {e}")
                return None

        return wrapper

    def get_bearer_token_func(self, bearer_func: Callable) -> Callable:
        """
        Get bearer token function wrapper for Django

        :param bearer_func: Original bearer function
        :return: Wrapped function
        """

        def wrapper(token: str) -> Optional[Dict[str, Any]]:
            try:
                return bearer_func(token)
            except Exception as e:
                logger.error(f"Error in bearer token function: {e}")
                return None

        return wrapper

    def get_api_key_func(self, api_key_func: Callable) -> Callable:
        """
        Get API key function wrapper for Django

        :param api_key_func: Original API key function
        :return: Wrapped function
        """

        def wrapper(
            api_key: str, required_scopes: Optional[list] = None
        ) -> Optional[Dict[str, Any]]:
            try:
                return api_key_func(api_key, required_scopes)
            except Exception as e:
                logger.error(f"Error in API key function: {e}")
                return None

        return wrapper

    def create_security_handler(
        self, security_scheme: Dict[str, Any], security_definition: Dict[str, Any]
    ) -> Optional[Callable]:
        """
        Create a security handler for the given scheme and definition

        :param security_scheme: Security scheme from OpenAPI spec
        :param security_definition: Security definition from OpenAPI spec
        :return: Security handler function or None
        """
        scheme_type = security_definition.get("type", "").lower()

        if scheme_type == "http":
            scheme = security_definition.get("scheme", "").lower()
            if scheme == "basic":
                return self._create_basic_auth_handler(
                    security_scheme, security_definition
                )
            elif scheme == "bearer":
                return self._create_bearer_token_handler(
                    security_scheme, security_definition
                )
        elif scheme_type == "apikey":
            return self._create_api_key_handler(security_scheme, security_definition)
        elif scheme_type == "oauth2":
            return self._create_oauth2_handler(security_scheme, security_definition)

        logger.warning(f"Unsupported security scheme type: {scheme_type}")
        return None

    def _create_basic_auth_handler(
        self, security_scheme: Dict[str, Any], security_definition: Dict[str, Any]
    ) -> Callable:
        """Create basic authentication handler"""

        def handler(request, *args, **kwargs):
            # Extract basic auth from Django request
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Basic "):
                return None

            try:
                import base64

                encoded_credentials = auth_header[6:]  # Remove 'Basic '
                credentials = base64.b64decode(encoded_credentials).decode("utf-8")
                username, password = credentials.split(":", 1)

                # Here you would typically validate against Django's auth system
                from django.contrib.auth import authenticate

                user = authenticate(request, username=username, password=password)

                if user and user.is_active:
                    return {"user": user, "username": username}
                return None

            except Exception as e:
                logger.error(f"Basic auth error: {e}")
                return None

        return handler

    def _create_bearer_token_handler(
        self, security_scheme: Dict[str, Any], security_definition: Dict[str, Any]
    ) -> Callable:
        """Create bearer token handler"""

        def handler(request, *args, **kwargs):
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return None

            token = auth_header[7:]  # Remove 'Bearer '

            # Here you would validate the token
            # This is a placeholder - implement your token validation logic
            try:
                # Example: validate JWT token or lookup in database
                # For now, just return the token
                return {"token": token}
            except Exception as e:
                logger.error(f"Bearer token validation error: {e}")
                return None

        return handler

    def _create_api_key_handler(
        self, security_scheme: Dict[str, Any], security_definition: Dict[str, Any]
    ) -> Callable:
        """Create API key handler"""
        key_name = security_definition.get("name", "X-API-Key")
        location = security_definition.get("in", "header")

        def handler(request, *args, **kwargs):
            api_key = None

            if location == "header":
                header_name = f'HTTP_{key_name.upper().replace("-", "_")}'
                api_key = request.META.get(header_name)
            elif location == "query":
                api_key = request.GET.get(key_name)
            elif location == "cookie":
                api_key = request.COOKIES.get(key_name)

            if not api_key:
                return None

            # Here you would validate the API key
            # This is a placeholder - implement your API key validation logic
            try:
                # Example: lookup API key in database
                return {"api_key": api_key}
            except Exception as e:
                logger.error(f"API key validation error: {e}")
                return None

        return handler

    def _create_oauth2_handler(
        self, security_scheme: Dict[str, Any], security_definition: Dict[str, Any]
    ) -> Callable:
        """Create OAuth2 handler"""

        def handler(request, *args, **kwargs):
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return None

            token = auth_header[7:]  # Remove 'Bearer '

            # Here you would validate the OAuth2 token
            # This is a placeholder - implement your OAuth2 validation logic
            try:
                # Example: introspect token with OAuth2 provider
                return {"token": token, "scopes": []}
            except Exception as e:
                logger.error(f"OAuth2 token validation error: {e}")
                return None

        return handler
