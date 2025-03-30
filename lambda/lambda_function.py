import boto3
import os
import base64
import json
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
kms_client = boto3.client('kms')

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    cmk_arn = os.environ['KMS_KEY_ARN']

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }

    if event["httpMethod"] == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            file_name = body.get("file_name")
            file_data = body.get("file_data")
            
            if not file_name or not file_data:
                return {
                    "statusCode": 400,
                    "headers": cors_headers,
                    "body": json.dumps({"error": "Missing file_name or file_data"}) 
                }
            
            # Decode base64 image data
            image_data = base64.b64decode(file_data)
            
            # Encrypt directly with KMS (for small files <4KB)
            encrypted = kms_client.encrypt(
                KeyId=cmk_arn,
                Plaintext=image_data
            )
            
            # Store encrypted data in S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=encrypted['CiphertextBlob'],
                Metadata={
                    'x-amz-meta-encryption-method': 'KMS_DIRECT'
                }
            )
            
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({
                    "message": "Image encrypted and stored successfully",
                    "file_name": file_name
                })
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({"error": str(e)})
            }
    
    elif event["httpMethod"] == "GET":
        try:
            # For GET requests, you'll need to implement decryption
            # Note: This is simplified - you'll need to adjust based on your needs
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            images = []
            
            if 'Contents' in response:
                for item in response['Contents']:
                    # Get the encrypted object
                    obj = s3_client.get_object(Bucket=bucket_name, Key=item['Key'])
                    ciphertext = obj['Body'].read()
                    
                    # Decrypt with KMS
                    decrypted = kms_client.decrypt(
                        KeyId=cmk_arn,
                        CiphertextBlob=ciphertext
                    )
                    
                    images.append({
                        'key': item['Key'],
                        'data': base64.b64encode(decrypted['Plaintext']).decode('utf-8'),
                        'lastModified': item['LastModified'].isoformat()
                    })
            
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({"images": images})
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({"error": str(e)})
            }