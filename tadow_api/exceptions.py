from typing import TYPE_CHECKING

from pydantic import ValidationError

if TYPE_CHECKING:
    from tadow_api.requests import HTTPRequest

from tadow_api.responses import HTTPResponse


class HttpException(Exception):
    status_code: int
    message: str

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        self.message = message


def handle_http_exception(
    exception: HttpException, request: "HTTPRequest"
) -> "HTTPResponse":
    return HTTPResponse(
        status_code=exception.status_code,
        raw_data=exception.message,
        content_type="application/json",
        headers=[],
    )


async def handle_validation_error(
    exception: ValidationError, request: "HTTPRequest"
) -> HTTPResponse:
    return HTTPResponse(
        status_code=400,
        raw_data=exception.json(),
        content_type="application/json",
        headers=[],
    )
