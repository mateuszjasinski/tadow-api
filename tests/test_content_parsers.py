import pytest

from tadow_api.content_parsers import ApplicationJsonParser
from tadow_api.exceptions import HttpException


def test_application_json_request_parser():
    raw_data = b'{"message": "Sample data", "value": 1}'
    parsed_data = ApplicationJsonParser.parse_request_data(raw_data)

    assert isinstance(parsed_data, dict)
    assert parsed_data == {"message": "Sample data", "value": 1}


def test_application_json_request_parser_exception():
    raw_data = b"Incorrect data"
    with pytest.raises(HttpException):
        ApplicationJsonParser.parse_request_data(raw_data)


def test_application_json_response_parser():
    raw_data = {"message": "Sample data", "value": 1}
    parsed = ApplicationJsonParser.parse_response_data(raw_data=raw_data)

    assert isinstance(parsed, bytes)
    assert parsed == b'{"message": "Sample data", "value": 1}'


@pytest.mark.skip
def test_application_xml_request_parser():
    pass


@pytest.mark.skip
def test_application_xml_request_parser_exception():
    pass


@pytest.mark.skip
def test_application_xml_response_parser():
    pass
