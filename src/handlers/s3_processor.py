import json
import logging
import os
import urllib.parse

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

s3_client = boto3.client("s3")


def lambda_handler(event: dict, context) -> dict:
    """Process S3 event notifications delivered via SQS."""
    logger.info("Received event: %s", json.dumps(event))

    # Record schema
    # https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-content-structure.html
    sqs_records = event.get("Records", [])
    processed = []

    for sqs_record in sqs_records:
        s3_event = json.loads(sqs_record["body"])
        for record in s3_event.get("Records", []):
            bucket = record["s3"]["bucket"]["name"]
            key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
            size = record["s3"]["object"].get("size", 0)
            event_name = record["eventName"]

            logger.info("Processing %s: s3://%s/%s (%d bytes)", event_name, bucket, key, size)

            result = process_object(bucket, key)
            processed.append(result)

    return {"statusCode": 200, "body": json.dumps({"processed": len(processed)})}


def process_object(bucket: str, key: str) -> dict:
    """Process a single S3 object."""
    response = s3_client.head_object(Bucket=bucket, Key=key)
    metadata = response.get("Metadata", {})

    logger.info("Object metadata: %s", metadata)

    # TODO: add processing logic here

    return {"bucket": bucket, "key": key, "metadata": metadata}
