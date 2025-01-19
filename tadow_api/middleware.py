from abc import abstractmethod, ABC

from tadow_api.requests import HTTPRequest
from tadow_api.responses import HTTPResponse


class BaseMiddleware(ABC):
    @abstractmethod
    def handle_request(self, request: HTTPRequest):
        pass

    @abstractmethod
    def handle_response(self, response: HTTPResponse):
        pass
