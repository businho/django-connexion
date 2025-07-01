"""
This module defines a Django Connexion API which implements translations between
Django and
Connexion requests / responses using direct OpenAPI specification parsing.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import path as django_path
from django.views.decorators.csrf import csrf_exempt

from django_connexion.apis import django_utils

logger = logging.getLogger("connexion.apis.django_api")


class DjangoApi:
    """
    Django API wrapper for Connexion 3.x that maintains backward compatibility
    """

    def __init__(
        self,
        specification: Union[str, Path, Dict],
        *args,
        name="django_connexion",
        **kwargs,
    ):
        self.name = name
        self._specification_path = specification
        self._url_patterns: list = []
        self._base_path = kwargs.get("base_path", "/")
        self._options = kwargs
        self._specification = None

        # Load the OpenAPI specification
        self._load_specification()

        # Add OpenAPI endpoints
        self.add_openapi_json()
        self.add_openapi_yaml()

        # Generate URL patterns from the specification
        self._generate_url_patterns()

    def _load_specification(self):
        """Load the OpenAPI specification from file or dict"""
        try:
            if isinstance(self._specification_path, dict):
                self._specification = self._specification_path
            else:
                spec_path = Path(self._specification_path)

                # If path is relative, make it absolute
                if not spec_path.is_absolute():
                    spec_path = Path.cwd() / spec_path

                if not spec_path.exists():
                    raise FileNotFoundError(
                        f"Specification file not found: {spec_path}"
                    )

                with open(spec_path, "r", encoding="utf-8") as f:
                    if spec_path.suffix.lower() in [".yaml", ".yml"]:
                        if HAS_YAML:
                            self._specification = yaml.safe_load(f)
                        else:
                            raise ImportError(
                                "PyYAML is required to load YAML specifications"
                            )
                    else:
                        self._specification = json.load(f)

        except Exception as e:
            logger.error(f"Failed to load specification: {e}")
            raise

    def add_openapi_json(self):
        """
        Adds openapi spec to {base_path}/openapi.json
        """
        self._url_patterns.append(
            django_path("openapi.json", self._get_openapi_json, name="openapi_json")
        )

    def add_openapi_yaml(self):
        """
        Adds spec yaml to {base_path}/openapi.yaml
        """
        self._url_patterns.append(
            django_path("openapi.yaml", self._get_openapi_yaml, name="openapi_yaml")
        )

    def _get_openapi_json(self, request):
        """Return OpenAPI spec as JSON"""
        try:
            return JsonResponse(self._specification)
        except Exception as e:
            logger.error(f"Error getting OpenAPI JSON: {e}")
            return JsonResponse(
                {"error": "Could not generate OpenAPI spec"}, status=500
            )

    def _get_openapi_yaml(self, request):
        """Return OpenAPI spec as YAML"""
        try:
            if HAS_YAML:
                yaml_content = yaml.dump(self._specification, default_flow_style=False)
                return HttpResponse(yaml_content, content_type="text/yaml")
            else:
                # Fallback to JSON if YAML is not available
                return JsonResponse(self._specification)
        except Exception as e:
            logger.error(f"Error getting OpenAPI YAML: {e}")
            return HttpResponse("Could not generate OpenAPI spec", status=500)

    @property
    def urls(self):
        """Return Django URL patterns"""
        return self._url_patterns, "django_connexion", self.name

    def _generate_url_patterns(self):
        """Generate Django URL patterns from OpenAPI specification"""
        try:
            if not self._specification:
                logger.warning("No specification loaded")
                return

            paths = self._specification.get("paths", {})
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.lower() in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "head",
                        "options",
                    ]:
                        self._add_operation(method.upper(), path, operation)

        except Exception as e:
            logger.error(f"Error generating URL patterns: {e}")

    def _add_operation(self, method: str, path: str, operation: Dict[str, Any]):
        """Add a single operation to URL patterns"""
        try:
            operation_id = operation.get("operationId")
            if not operation_id:
                logger.warning(f"No operationId found for {method} {path}")
                return

            # Convert OpenAPI path to Django path
            path_param_types = self._get_path_parameter_types(operation, path)
            django_path_str = django_utils.djangofy_path(path, path_param_types)

            # Create the view function
            view_func = self._create_view_function(
                operation_id, method, path, operation
            )

            # Create Django URL pattern
            endpoint_name = django_utils.djangofy_endpoint(operation_id, None)
            url_pattern = django_path(
                django_path_str.lstrip("/"), view_func, name=endpoint_name
            )

            self._url_patterns.append(url_pattern)
            logger.debug(
                f"Added URL pattern: {method} {django_path_str} -> {operation_id}"
            )

        except Exception as e:
            logger.error(f"Error adding operation {method} {path}: {e}")

    def _get_path_parameter_types(
        self, operation: Dict[str, Any], path: str
    ) -> Dict[str, str]:
        """Extract path parameter types from operation and path"""
        param_types = {}

        # Get parameters from operation
        parameters = operation.get("parameters", [])
        for param in parameters:
            if param.get("in") == "path":
                name = param.get("name")
                schema = param.get("schema", {})
                param_type = schema.get("type", "string")
                param_types[name] = param_type

        # Also check global parameters in path item
        # This is not implemented in the current spec but keeping for completeness

        return param_types

    def _create_view_function(
        self, operation_id: str, method: str, path: str, operation: Dict[str, Any]
    ):
        """Create a Django view function that delegates to the original handler"""

        @csrf_exempt
        def view_func(request: HttpRequest, **kwargs):
            try:
                # Import and get the actual handler function
                handler_func = self._import_handler(operation_id)
                if not handler_func:
                    return HttpResponse("Handler not found", status=500)

                # Convert path parameters from Django format to what the handler expects
                converted_kwargs = self._convert_path_params(kwargs)

                # Parse query parameters
                query_params = self._process_query_params(request, operation)

                # Merge path params and query params for the handler
                all_params = {**converted_kwargs, **query_params}

                # Call the handler with Django request and parameters
                if method.upper() in ["GET", "DELETE", "HEAD", "OPTIONS"]:
                    # For methods without body, pass request and all params as kwargs
                    result = handler_func(request, **all_params)
                else:
                    # For methods with potential body, pass request and all params
                    result = handler_func(request, **all_params)

                # Convert result to Django response if needed
                return self._convert_to_django_response(result)

            except Exception as e:
                logger.error(f"Error in view function for {operation_id}: {e}")
                return HttpResponse("Internal Server Error", status=500)

        # Add method checking
        def method_restricted_func(request, **kwargs):
            if request.method.upper() != method.upper():
                from django.http import HttpResponseNotAllowed

                return HttpResponseNotAllowed([method.upper()])
            return view_func(request, **kwargs)

        return method_restricted_func

    def _process_query_params(
        self, request: HttpRequest, operation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process query parameters according to OpenAPI specification"""
        processed = {}

        # Get parameter definitions from operation
        param_definitions = {}
        for param in operation.get("parameters", []):
            if param.get("in") == "query":
                param_definitions[param.get("name")] = param

        # Process each parameter in the request
        for name in request.GET.keys():
            if name in param_definitions:
                param_def = param_definitions[name]
                schema = param_def.get("schema", {})

                # Handle array parameters
                if schema.get("type") == "array":
                    # Use getlist to get all values for array parameters
                    processed[name] = request.GET.getlist(name)
                else:
                    # Use get for single values
                    processed[name] = request.GET.get(name)
            else:
                # For parameters not in spec, use single value
                processed[name] = request.GET.get(name)

        return processed

    def _import_handler(self, operation_id: str):
        """Import and return the handler function"""
        try:
            if "." not in operation_id:
                return None

            module_path, function_name = operation_id.rsplit(".", 1)

            # Import the module
            import importlib

            module = importlib.import_module(module_path)

            # Get the function
            handler_func = getattr(module, function_name)
            return handler_func

        except (ImportError, AttributeError) as e:
            logger.error(f"Could not import handler {operation_id}: {e}")
            return None

    def _convert_path_params(self, django_params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Django path parameters to the format expected by handlers"""
        # Convert parameter names from Django format to original format
        converted = {}
        for key, value in django_params.items():
            # Replace underscores with hyphens if needed
            converted[key] = value
        return converted

    def _convert_to_django_response(self, result):
        """Convert handler result to Django response"""
        if isinstance(result, (HttpResponse, JsonResponse)):
            return result
        elif isinstance(result, str):
            return HttpResponse(result)
        elif isinstance(result, (dict, list)):
            return JsonResponse(result)
        else:
            return HttpResponse(str(result))

    @classmethod
    def get_request(cls, request, *args, **params):
        """
        This method converts Django request to a ConnexionRequest for compatibility.
        Note: This is kept for compatibility but may not be used in Connexion 3.x
        """
        try:
            from connexion.lifecycle import ConnexionRequest

            context_dict = {"request": request}
            body = request.body

            connexion_request = ConnexionRequest(
                request.path,
                request.method,
                headers=dict(request.headers),
                form=dict(request.POST),
                query=dict(request.GET),
                body=body,
                json_getter=lambda: (
                    request.content_type == "application/json" and json.loads(body)
                    if body
                    else None
                ),
                files=dict(request.FILES),
                path_params=params,
                context=context_dict,
            )

            logger.debug(
                "Getting data and status code",
                extra={
                    "data": connexion_request.body,
                    "data_type": type(connexion_request.body),
                    "url": connexion_request.url,
                },
            )
            return connexion_request
        except ImportError:
            # If ConnexionRequest is not available, return None
            logger.warning(
                "ConnexionRequest not available, " "compatibility method disabled"
            )
            return None

    @classmethod
    def get_response(cls, response, mimetype=None, request=None):
        """
        This method converts a handler response to a framework response.
        Kept for backward compatibility.
        """
        return cls._get_response(response, mimetype=mimetype)

    @classmethod
    def _is_framework_response(cls, response):
        """Return True if `response` is a Django response class"""
        return django_utils.is_django_response(response)

    @classmethod
    def _framework_to_connexion_response(cls, response, mimetype):
        """Cast Django response class to ConnexionResponse used for schema validation"""
        pass

    @classmethod
    def _connexion_to_framework_response(cls, response, mimetype, extra_context=None):
        """Cast ConnexionResponse to Django response class"""
        pass

    @classmethod
    def _build_response(
        cls,
        data,
        mimetype,
        content_type=None,
        status_code=None,
        headers=None,
        extra_context=None,
    ):
        """
        Create a Django response from the provided arguments.
        """
        if isinstance(data, (dict, list)):
            response = JsonResponse(data, status=status_code or 200)
        else:
            response = HttpResponse(
                data, content_type=content_type or mimetype, status=status_code or 200
            )

        if headers:
            for key, value in headers.items():
                response[key] = value

        return response

    @classmethod
    def _get_response(cls, response, mimetype=None):
        """Convert response to Django response"""
        if cls._is_framework_response(response):
            return response

        return cls._build_response(response, mimetype)
