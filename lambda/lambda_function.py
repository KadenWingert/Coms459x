import boto3
import os
import base64

s3 = boto3.client('s3')

def upload_image_to_s3(file_name, bucket_name, file_data=None):
    """Uploads an image to S3."""
    if file_data:
        # Fix incorrect padding if needed
        missing_padding = len(file_data) % 4
        if missing_padding:
            file_data += '=' * (4 - missing_padding)  # Add necessary padding to the base64 string
        
        # Decode base64 data if provided
        file_data = base64.b64decode(file_data)
        file_name_with_extension = file_name.split('.')[0] + '.jpg'  # Ensure the file has an extension

        # Upload to S3
        s3.put_object(Bucket=bucket_name, Key=file_name_with_extension, Body=file_data)
        return file_name_with_extension
    else:
        # If file is to be fetched from the Lambda environment, ensure it's in `/tmp` first
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                s3.upload_fileobj(f, bucket_name, file_name)
            return file_name
        else:
            raise Exception("File does not exist in /tmp or the path provided.")

def get_image_from_s3(bucket_name, file_name):
    """Retrieves an image from S3."""
    local_file_path = f"/tmp/{file_name}"  # Lambda allows temporary storage in /tmp
    s3.download_file(bucket_name, file_name, local_file_path)
    return local_file_path

def delete_image_from_s3(bucket_name, file_name):
    """Deletes an image from S3."""
    s3.delete_object(Bucket=bucket_name, Key=file_name)

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    action = event.get("action")  # This is a custom parameter to define the action

    # Example event format:
    # { "action": "upload", "file_name": "image.jpg" }

    if action == "upload":
        file_name = event.get("file_name")
        file_data = event.get("file_data")  # This can be base64 data if uploaded via the front-end
        
        uploaded_file = upload_image_to_s3(file_name, bucket_name, file_data=file_data)
        return {
            "statusCode": 200,
            "body": f"Image {uploaded_file} uploaded successfully!"
        }

    elif action == "get":
        file_name = event.get("file_name")
        local_file_path = get_image_from_s3(bucket_name, file_name)
        return {
            "statusCode": 200,
            "body": f"Image {file_name} retrieved to {local_file_path}."
        }

    elif action == "delete":
        file_name = event.get("file_name")
        delete_image_from_s3(bucket_name, file_name)
        return {
            "statusCode": 200,
            "body": f"Image {file_name} deleted successfully!"
        }

    else:
        return {
            "statusCode": 400,
            "body": "Invalid action. Use 'upload', 'get', or 'delete'."
        }
