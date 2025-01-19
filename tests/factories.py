from tadow_api.requests import HTTPRequest, Cookie


def create_mock_request(
    url: str = "/",
    http_method: str = "GET",
    content_type: str = "application/json",
    raw_data: dict | None = None,
    cookies: dict[str, Cookie] | None = None,
) -> HTTPRequest:
    return HTTPRequest(
        http_method=http_method,
        content_type=content_type,
        url=url,
        raw_data=raw_data or {},
        cookies=cookies or {},
    )
