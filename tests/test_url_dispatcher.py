import pytest

from tadow_api.exceptions import HttpException
from tadow_api.responses import HTTPResponse
from tadow_api.url_dispatcher import APIRoute, RegexURLDispatcher
from tests.factories import create_mock_request


def example_function():
    return HTTPResponse(
        status_code=200, raw_data="Root", content_type="application/json", headers=[]
    )


root_route = APIRoute(endpoint_func=example_function, path="/")

variable_route = APIRoute(endpoint_func=example_function, path="/(?P<variable>[^/]+)")

items_route = APIRoute(endpoint_func=example_function, path="/items")

registered_routes = {
    "/": root_route,
    "/(?P<variable>[^/]+)": variable_route,
    "/items": items_route,
}
regex_dispatcher = RegexURLDispatcher()


# TODO Create single request mock factory
class RequestMock:
    def __init__(self, url: str, http_method: str | None = None):
        self.http_method = http_method or "GET"
        self.url = url

    def validate_request_data(self, validation_model) -> None:
        pass


def test_route_found():
    route, _ = regex_dispatcher(
        registered_routes=registered_routes, request=create_mock_request(url="/")
    )
    assert route == root_route

    route, _ = regex_dispatcher(
        registered_routes=registered_routes, request=create_mock_request(url="/index")
    )
    assert route == variable_route

    route, _ = regex_dispatcher(
        registered_routes=registered_routes, request=create_mock_request(url="/items")
    )
    assert route == items_route


def test_not_found():
    with pytest.raises(HttpException):
        route, _ = regex_dispatcher(
            registered_routes=registered_routes,
            request=create_mock_request(url="/api/tests"),
        )


def test_method_not_allowed():
    with pytest.raises(HttpException):
        route, _ = regex_dispatcher(
            registered_routes=registered_routes,
            request=create_mock_request(url="/test", http_method="POST"),
        )
