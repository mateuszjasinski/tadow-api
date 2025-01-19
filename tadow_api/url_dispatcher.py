import re
from abc import ABC, abstractmethod
from typing import Any

from tadow_api.exceptions import HttpException
from tadow_api.requests import HTTPRequest
from tadow_api.routing import APIRoute


class BaseURLDispatcher(ABC):
    @abstractmethod
    def __call__(
        self, registered_routes: dict[str, APIRoute], request: HTTPRequest
    ) -> tuple[APIRoute, dict[Any]] | None:
        raise NotImplementedError


class RegexURLDispatcher:
    def __call__(
        self, registered_routes: dict[str, APIRoute], request: HTTPRequest
    ) -> tuple[APIRoute, dict[Any]] | None:
        matching_paths: list[tuple[str, re.Match]] = []

        for path in registered_routes.keys():
            match: re.Match = re.match(path, request.url)
            if match and len(match.group()) >= len(request.url):
                matching_paths.append((path, match))

        if not matching_paths:
            raise HttpException(message="Not found", status_code=404)

        # Find best path
        best_path, match = sorted(
            matching_paths,
            key=lambda items: len(items[1].groups()),
        )[0]

        route: APIRoute = registered_routes.get(best_path)

        if request.http_method not in route.methods:
            raise HttpException(message="Method not allowed", status_code=403)

        return route, match.groupdict()
