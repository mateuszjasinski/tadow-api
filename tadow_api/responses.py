from typing import Any, TYPE_CHECKING, Type

from pydantic import BaseModel

from tadow_api.config import app_config
from tadow_api.content_parsers import ContentParser

if TYPE_CHECKING:
    from tadow_api.requests import HTTPRequest


_SIMPLE_TYPES = [int, str, dict, list]


class HTTPResponse:
    def __init__(
        self,
        status_code: int,
        raw_data: _SIMPLE_TYPES,
        headers: list[tuple[str, str]],
        content_type: str | None = None,
    ):
        self.status_code = status_code
        self.raw_data = raw_data
        self.content_type = content_type or app_config().default_content_type
        self.headers = headers

    async def send_response(self, send):
        response_body: bytes = ContentParser.parse_response(
            content_type=self.content_type, raw_data=self.raw_data
        )

        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": [[b"content-type", self.content_type]],
            }
        )
        await send({"type": "http.response.body", "body": response_body})

    @classmethod
    def create_response(
        cls,
        request: "HTTPRequest",
        validation_model: BaseModel | Type[BaseModel] | None = None,
        *args: Any,
    ) -> "HTTPResponse":
        # Unpack function response
        function_response, status_code, cookies = tuple(list(*args) + [None] * 3)[:3]

        # Serialize response to bytes
        raw_data = function_response
        if isinstance(function_response, BaseModel):
            raw_data = function_response.model_dump()

        # Validate response
        if validation_model:
            raw_data = validation_model(raw_data).model_dump()

        return cls(
            status_code=status_code or 200,
            content_type=request.content_type,
            raw_data=raw_data,
            headers=[
                # ('cookies', )
            ],
        )
