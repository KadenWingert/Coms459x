import boto3
import os
import base64
import json
from botocore.exceptions import ClientError
import logging

from botocore.client import Config
s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))


# Initialize clients
# s3_client = boto3.client('s3')

kms_client = boto3.client('kms')  # KMS client to perform encryption and decryption
bucket_name = os.environ['BUCKET_NAME']
kms_key_arn = os.environ['KMS_KEY_ARN']

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def lambda_handler(event, context):
    logger.info("Lambda handler invoked.")

    query_params = event.get("queryStringParameters") or {}

    if event["httpMethod"] == "POST":
        return store_image(event)
    elif event["httpMethod"] == "GET":
        if "key" in query_params:
            return get_signed_url(query_params["key"])
        else:
            return retrieve_images()
    elif event["httpMethod"] == "DELETE":
        return delete_image(event)
    else:
        return {"statusCode": 400, "headers": cors_headers, "body": json.dumps({"error": "Unsupported method"})}


def store_image(event):
    try:
        body = json.loads(event.get("body", "{}"))
        file_name = body.get("file_name")
        file_data = body.get("file_data")
        logger.debug(f"File name: {file_name}")

        if not file_name or not file_data:
            return {"statusCode": 400, "headers": cors_headers, "body": json.dumps({"error": "Missing file_name or file_data"})}

        # Decode base64 image data
        image_data = base64.b64decode(file_data)
        logger.debug(f"Image data length: {len(image_data)}")

        # Encrypt metadata using AWS KMS
        metadata = json.dumps({"file_name": file_name}).encode('utf-8')
        response = kms_client.encrypt(
            KeyId=kms_key_arn,
            Plaintext=metadata
        )
        encrypted_metadata = base64.b64encode(response['CiphertextBlob']).decode('utf-8')

        # Store image in S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_data,
            Metadata={'encrypted_metadata': encrypted_metadata}
        )

        return {"statusCode": 200, "headers": cors_headers, "body": json.dumps({"message": "Image stored successfully", "file_name": file_name})}

    except Exception as e:
        logger.error(f"Error storing image: {e}")
        return {"statusCode": 500, "headers": cors_headers, "body": json.dumps({"error": str(e)})}


def get_signed_url(file_key):
    logger.info("IN GET_SINGNED_URL.")
    try:
        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        logger.info(f"GENERATED SIGNED URL: {signed_url}")


        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"signed_url": signed_url})
        }

    except Exception as e:
        logger.error(f"Failed to generate signed URL: {e}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }


def retrieve_images():
    logger.info("IN RETRIEVE_IMAGES.")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        if "Contents" not in response:
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({"images": []})
            }

        images = []
        for obj in response["Contents"]:
            file_key = obj["Key"]
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": file_key},
                ExpiresIn=3600  # URL valid for 1 hour
            )

            images.append({
                "key": file_key,
                "imageUrl": presigned_url,
                "lastModified": obj["LastModified"].isoformat()
            })

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"images": images})
        }

    except ClientError as e:
        logger.error(f"Failed to list images: {e}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": "Failed to retrieve images"})
        }
    
def delete_image(event):
    try:
        #the key is the name of the image you wish to delete
        query_params = event.get("queryStringParameters") or {}
        file_key = query_params.get("key")

        if not file_key:
            return {"statusCode": 400, "headers": cors_headers, "body": json.dumps({"error": "Missing 'key' parameter"})}

        #try and delete the bucket via the key
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"message": f"Image '{file_key}' deleted successfully"})
        }

    except Exception as e:
        logger.error(f"Failed to delete image: {e}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }
