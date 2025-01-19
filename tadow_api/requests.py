from typing import Callable, Type, TYPE_CHECKING

from pydantic import BaseModel

from tadow_api.content_parsers import ContentParser

if TYPE_CHECKING:
    from tadow_api.middleware import BaseMiddleware


def get_header_from_scope(scope: dict, key: str) -> str | None:
    """
    Method used to get header by name from scope.
    :param scope: Scope dict
    :param key: Name of header
    :return: Value of header
    """
    try:
        raw_header: bytes = next(
            filter(
                lambda header: header[0] == key.encode("utf-8"), scope.get("headers")
            )
        )[1]
        return raw_header.decode("utf-8")
    except (StopIteration, KeyError):
        return None


class Cookie:
    def __init__(
        self,
        name: str,
        value: str,
        expires: str | None = None,
        domain: str | None = None,
        secure: str | None = None,
        http_only: bool = False,
    ):
        self.name = name
        self.value = value
        self.expires = expires
        self.domain = domain
        self.secure = secure
        self.http_only = http_only

    @classmethod
    def parse_cookies_from_header(cls, header_value: str | None) -> dict[str, "Cookie"]:
        cookies = {}
        if not header_value:
            return cookies

        for raw_cookie in header_value.split("; "):
            cookie_name, cookie_value = raw_cookie.split("=")
            cookies[cookie_name] = Cookie(cookie_name, cookie_value)
        return cookies


class HTTPRequest:
    def __init__(
        self,
        http_method: str,
        url: str,
        cookies: dict[str, Cookie],
        content_type: str,
        raw_data: dict,
    ):
        self.http_method = http_method
        self.url = url
        self.cookies = cookies
        self.content_type = content_type

        # Data fields
        self._raw_data = raw_data
        self.data = None

    def validate_request_data(
        self, validation_model: BaseModel | Type[BaseModel] | None
    ) -> None:
        if not self._raw_data:
            return

        if validation_model:
            self.data = validation_model(**self._raw_data)
        else:
            self.data = self._raw_data

    @classmethod
    async def create_request(
        cls, scope: dict, receive: Callable, middlewares: list["BaseMiddleware"]
    ) -> "HTTPRequest":
        request_raw_data: dict = await receive()
        content_type = get_header_from_scope(scope, "content-type")

        request_instance: HTTPRequest = cls(
            http_method=scope.get("method"),
            url=scope.get("path"),
            cookies=Cookie.parse_cookies_from_header(
                get_header_from_scope(scope, "cookies")
            ),
            content_type=content_type,
            raw_data=ContentParser.parse_request(
                raw_data=request_raw_data.get("body"), content_type=content_type
            ),
        )

        for middleware in middlewares:
            middleware.handle_request(request=request_instance)

        return request_instance
