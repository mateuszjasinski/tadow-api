from typing import Type, Callable

from pydantic import ValidationError

from tadow_api.config import Config, set_default_config, get_default_config
from tadow_api.exceptions import HttpException, handle_validation_error
from tadow_api.middleware import BaseMiddleware
from tadow_api.requests import HTTPRequest
from tadow_api.responses import HTTPResponse
from tadow_api.routing import APIRoute, Router
from tadow_api.url_dispatcher import RegexURLDispatcher, BaseURLDispatcher


class TadowAPI(Router):
    _custom_exception_handlers: dict[Type[Exception], Callable]
    _middlewares: list[BaseMiddleware]

    def __init__(
        self,
        url_dispatcher: BaseURLDispatcher = RegexURLDispatcher(),
        middlewares: list[BaseMiddleware] | None = None,
        prefix: str | None = None,
        app_config: Config | None = None,
    ):
        super().__init__(prefix)
        self._url_dispatched = url_dispatcher
        self._custom_exception_handlers = {ValidationError: handle_validation_error}

        if not middlewares:
            self._middlewares = []

        if app_config:
            set_default_config(config=app_config)

    def register_router(self, router: Router) -> None:
        """
        Method used to add all registered routes from Router to main app.
        :param router: Router instance
        """
        if not hasattr(self, "_registered_routes") or self._registered_routes is None:
            self._registered_routes = {}

        for path, route in router.get_registered_routes().items():
            full_route_path = f"{self.prefix}{path}"
            if full_route_path in self._registered_routes:
                raise AttributeError(f"{full_route_path} already registered")
            self._registered_routes[full_route_path] = route

    @staticmethod
    def request_response_handler(func):
        async def decorator(self, scope, receive, send):
            # Build request
            try:
                request: HTTPRequest = await HTTPRequest.create_request(
                    scope, receive, self._middlewares
                )

                route, arguments = self._url_dispatched(
                    self.get_registered_routes(), request
                )
            except HttpException as exception:
                await HTTPResponse(
                    status_code=exception.status_code,
                    raw_data=exception.message,
                    headers=[],
                ).send_response(send)
                return

            # Call function
            try:
                response = await func(self, route, request, **arguments)

                for middleware in self._middlewares:
                    middleware.handle_response(response)
                await response.send_response(send)
            except Exception as exc:
                if get_default_config().debug:
                    import traceback

                    error_content = traceback.format_exc()
                else:
                    error_content = "Internal server error"
                await HTTPResponse(
                    status_code=500,
                    headers=[],
                    raw_data=error_content,
                ).send_response(send)
                raise exc

        return decorator

    @request_response_handler
    async def __call__(
        self, route: APIRoute, request: HTTPRequest, *args, **kwargs
    ) -> HTTPResponse:
        try:
            return await route(request, *args, **kwargs)
        except Exception as exc:
            if type(exc) in self._custom_exception_handlers:
                return await self._custom_exception_handlers[type(exc)](exc, request)
            raise exc
