import boto3
import os
import base64
import json

s3 = boto3.client('s3')

# CORS Headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # Allow any origin
    "Access-Control-Allow-Methods": "OPTIONS, GET, POST, DELETE",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json"
}

def upload_image_to_s3(file_name, bucket_name, file_data=None):
    """Uploads an image to S3."""
    if file_data:
        # Fix incorrect padding if needed
        missing_padding = len(file_data) % 4
        if missing_padding:
            file_data += '=' * (4 - missing_padding)  # Add necessary padding
        
        # Decode base64 data if provided
        file_data = base64.b64decode(file_data)
        file_name_with_extension = file_name.split('.')[0] + '.jpg'  # Ensure a proper extension

        # Upload to S3
        s3.put_object(Bucket=bucket_name, Key=file_name_with_extension, Body=file_data)
        return file_name_with_extension
    else:
        if os.path.exists(file_name):  # Handle file upload from Lambda storage
            with open(file_name, 'rb') as f:
                s3.upload_fileobj(f, bucket_name, file_name)
            return file_name
        else:
            raise Exception("File does not exist in /tmp or the path provided.")

def get_image_from_s3(bucket_name, file_name):
    """Retrieves an image from S3."""
    local_file_path = f"/tmp/{file_name}"
    s3.download_file(bucket_name, file_name, local_file_path)
    return local_file_path

def delete_image_from_s3(bucket_name, file_name):
    """Deletes an image from S3."""
    s3.delete_object(Bucket=bucket_name, Key=file_name)



def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']

    # ✅ Handle CORS Preflight Requests
    if event["httpMethod"] == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, GET, POST, DELETE",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"message": "CORS preflight success"})
        }

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Invalid JSON format"})
        }

    if event["httpMethod"] == "POST":
        file_name = body.get("file_name")
        file_data = body.get("file_data")

        if not file_name or not file_data:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Missing 'file_name' or 'file_data'"})
            }

        uploaded_file = upload_image_to_s3(file_name, bucket_name, file_data)
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": f"Image '{uploaded_file}' uploaded successfully!"})
        }
    
    return {
        "statusCode": 400,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": "Invalid HTTP method"})
    }
