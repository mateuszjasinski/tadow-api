import asyncio
import inspect
from typing import Callable, Type

from pydantic import BaseModel

from tadow_api.requests import HTTPRequest
from tadow_api.responses import HTTPResponse


class APIRoute:
    def __init__(
        self,
        path: str,
        endpoint_func: Callable,
        methods: list[str] | None = None,
        request_model: BaseModel | Type[BaseModel] | None = None,
        response_model: BaseModel | Type[BaseModel] | None = None,
    ):
        self.path = path
        self.endpoint_func = endpoint_func
        self.methods = methods or ["GET"]
        self.request_model = request_model
        self.response_model = response_model

    def _check_endpoint_arguments(self, request: HTTPRequest, **kwargs):
        signature = inspect.signature(self.endpoint_func)
        extended_kwargs = {"request": request, **kwargs}

        if len(signature.parameters) <= 0:
            return {}
        # Create dict of all available arguments and return all that match signature
        function_arguments = {}

        parameter: inspect.Parameter
        for _, parameter in signature.parameters.items():
            # Perform mapping, if parameter is annotated
            if parameter.annotation is not parameter.empty:
                function_arguments[parameter.name] = parameter.annotation(
                    extended_kwargs[parameter.name]
                )
            else:
                function_arguments[parameter.name] = extended_kwargs[parameter.name]

        return function_arguments

    async def __call__(self, request: HTTPRequest, *args, **kwargs):
        # Validate request data
        request.validate_request_data(validation_model=self.request_model)

        # Call endpoint function
        function_arguments = self._check_endpoint_arguments(request=request, **kwargs)

        # Call async of sync
        if asyncio.iscoroutinefunction(self.endpoint_func):
            content = await self.endpoint_func(**function_arguments)
        else:
            content = self.endpoint_func(**function_arguments)

        return HTTPResponse.create_response(request, self.response_model, content)

    def __eq__(self, other: "APIRoute"):
        return self.path == other.path

    def __repr__(self) -> str:
        return f"<APIRoute path: {self.path} >"


class Router:
    _registered_routes: dict[str, APIRoute]

    def __init__(self, prefix: str | None = None):
        self.prefix = prefix

    def get_registered_routes(self) -> dict[str, APIRoute]:
        return self._registered_routes

    def _register_new_endpoint(
        self,
        path: str,
        endpoint_func: Callable,
        methods: list[str] | None = None,
        request_model: BaseModel | Type[BaseModel] | None = None,
        response_model: BaseModel | Type[BaseModel] | None = None,
    ):
        full_route_path = f"{self.prefix}{path}"

        self._registered_routes[full_route_path] = APIRoute(
            path=full_route_path,
            endpoint_func=endpoint_func,
            methods=methods,
            request_model=request_model,
            response_model=response_model,
        )

    def endpoint(
        self,
        path: str,
        methods: list[str] | None = None,
        request_model: BaseModel | Type[BaseModel] | None = None,
        response_model: BaseModel | Type[BaseModel] | None = None,
    ):
        def decorator(endpoint_func):
            if (
                not hasattr(self, "_registered_routes")
                or self._registered_routes is None
            ):
                self._registered_routes = {}

            # Add path to registered
            self._register_new_endpoint(
                path=path,
                endpoint_func=endpoint_func,
                methods=methods,
                request_model=request_model,
                response_model=response_model,
            )

            return endpoint_func

        return decorator
