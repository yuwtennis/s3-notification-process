import json
from unittest import mock

import pytest

from src.handlers.s3_processor import lambda_handler, process_object


@pytest.fixture
def sqs_event():
    with open("events/sqs-event.json") as f:
        return json.load(f)


@pytest.fixture
def lambda_context():
    context = mock.MagicMock()
    context.function_name = "s3-notification-process"
    context.aws_request_id = "test-request-id"
    return context


def test_lambda_handler_returns_200(sqs_event, lambda_context):
    with mock.patch("src.handlers.s3_processor.s3_client") as mock_s3:
        mock_s3.head_object.return_value = {"Metadata": {}}
        response = lambda_handler(sqs_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["processed"] == 1


def test_lambda_handler_empty_records(lambda_context):
    event = {"Records": []}
    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["processed"] == 0


def test_lambda_handler_empty_s3_records_in_sqs(lambda_context):
    event = {
        "Records": [
            {
                "body": json.dumps({"Records": []}),
                "eventSource": "aws:sqs",
            }
        ]
    }
    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["processed"] == 0


def test_process_object_returns_metadata():
    with mock.patch("src.handlers.s3_processor.s3_client") as mock_s3:
        mock_s3.head_object.return_value = {"Metadata": {"foo": "bar"}}
        result = process_object("my-bucket", "path/to/file.txt")

    assert result["bucket"] == "my-bucket"
    assert result["key"] == "path/to/file.txt"
    assert result["metadata"] == {"foo": "bar"}