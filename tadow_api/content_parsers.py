import json
import xml.parsers.expat

import xmltodict
from abc import ABC, abstractmethod
from typing import Type

from tadow_api.config import app_config


class BaseParser(ABC):
    @classmethod
    @abstractmethod
    def parse_request_data(cls, raw_data: bytes) -> dict:
        pass

    @classmethod
    @abstractmethod
    def parse_response_data(cls, raw_data: dict) -> bytes:
        pass


class ContentParser:
    _registered_parser: dict[str, BaseParser | Type[BaseParser]]

    @classmethod
    def register_parser(cls, content_type: str):
        def decorator(obj):
            if not hasattr(cls, "_registered_parser") or cls._registered_parser is None:
                cls._registered_parser = {}

            cls._registered_parser[content_type] = obj
            return obj

        return decorator

    @classmethod
    def parse_request(cls, raw_data: bytes, content_type: str) -> dict:
        if content_type not in cls._registered_parser:
            raise AttributeError("Content type not supported!")
        parser: BaseParser = cls._registered_parser[content_type]
        return parser.parse_request_data(raw_data=raw_data)

    @classmethod
    def parse_response(cls, raw_data: dict, content_type: str) -> bytes:
        if content_type not in cls._registered_parser:
            raise AttributeError("Content type not supported!")
        parser: BaseParser = cls._registered_parser[content_type]
        return parser.parse_response_data(raw_data=raw_data)


@ContentParser.register_parser(content_type="application/json")
class ApplicationJsonParser(BaseParser):
    @classmethod
    def parse_request_data(cls, raw_data: bytes) -> dict:
        try:
            return json.loads(raw_data.decode(app_config().default_encoding))
        except json.JSONDecodeError:
            from tadow_api.exceptions import HttpException

            raise HttpException(status_code=400, message="Invalid request data")

    @classmethod
    def parse_response_data(cls, raw_data: dict) -> bytes:
        return json.dumps(raw_data).encode(app_config().default_encoding)


@ContentParser.register_parser(content_type="application/xml")
class ApplicationXMLParser(BaseParser):
    @classmethod
    def parse_request_data(cls, raw_data: bytes) -> dict:
        try:
            return xmltodict.parse(raw_data, encoding=app_config().default_encoding)
        except xml.parsers.expat.ExpatError:
            from tadow_api.exceptions import HttpException

            raise HttpException(status_code=400, message="Invalid request data")

    @classmethod
    def parse_response_data(cls, raw_data: dict) -> bytes:
        from dicttoxml import dicttoxml

        return dicttoxml(
            raw_data, encoding=app_config().default_encoding, return_bytes=True
        )
