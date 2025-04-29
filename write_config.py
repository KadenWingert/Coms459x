import boto3
import json
import os

# Ensure to use the session correctly for both profile and region
session = boto3.Session(profile_name='kadenwin', region_name='us-east-1')
cloudformation = session.client('cloudformation')
s3 = session.client('s3')  
lambda_client = session.client('lambda')

stack_name = 'ImageStorageS3Stack'  

# Find the Lambda function
response = lambda_client.list_functions()
lambda_function_name = None
for function in response['Functions']:
    if function['FunctionName'].startswith('ImageHandlerLambda') and function['Runtime'].startswith('python'):
        lambda_function_name = function['FunctionName']
        break

if lambda_function_name:
    print(f"Found function: {lambda_function_name}")

try:
    # Fetch stack outputs
    response = cloudformation.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']

    # Get API URL
    api_url = next(
        (output['OutputValue'] for output in outputs if output['OutputKey'] == 'ApiUrl'), 
        None
    )

    if not api_url:
        print("❌ API URL output not found in stack.")
        exit(1)

    # Find the website bucket
    buckets_response = s3.list_buckets()
    bucket_name = next(
        (bucket['Name'] for bucket in buckets_response['Buckets'] if 'websitebucket' in bucket['Name']),
        None
    )

    if not bucket_name:
        print("❌ No S3 bucket found with 'websitebucket' in its name.")
        exit(1)

    # Config data to write
    config_data = {'API_URL': api_url}

    # --- Update both config.json locations ---
    config_locations = [
        'config.json',          # Root level
        'website_assets/public/config.json'    # Public folder (for React/Vue apps)
    ]

    for config_path in config_locations:
        # 1. Write locally (optional)
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file)
        print(f"✅ Local {config_path} updated")

        # 2. Upload to S3
        try:
            s3.upload_file(
                Filename=config_path,
                Bucket=bucket_name,
                Key=config_path
            )
            print(f"✅ Uploaded {config_path} to S3 bucket: {bucket_name}")
        except Exception as e:
            print(f"⚠️ Failed to upload {config_path}: {str(e)}")

except Exception as e:
    print(f"🚨 Error: {e}")
    exit(1)