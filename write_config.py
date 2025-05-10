import boto3
import json
import os

# Ensure to use the session correctly for both profile and region
session = boto3.Session(profile_name='crun', region_name='us-east-1')
cloudformation = session.client('cloudformation')
s3 = session.client('s3')  
lambda_client = session.client('lambda')

stack_name = 'ImageStorageS3Stack'  

response = lambda_client.list_functions()


# Find the Lambda function that starts with 'ImageHandlerLambda'
lambda_function_name = None
for function in response['Functions']:
    if function['FunctionName'].startswith('ImageHandlerLambda') and function['Runtime'].startswith('python'):
        lambda_function_name = function['FunctionName']
        break

# Check if a function was found
if lambda_function_name:
    print(f"Found function: {lambda_function_name}")

try:
    # Fetch stack outputs
    response = cloudformation.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']

    # Initialize variable to store API URL
    api_url = None

    # Search for API URL in the stack outputs
    for output in outputs:
        if output['OutputKey'] == 'ApiUrl':
            api_url = output['OutputValue']

    if api_url:
        # Get list of all buckets in the current region
        buckets_response = s3.list_buckets()
        bucket_name = None

        # Search for a bucket name that contains 'websitebucket'
        for bucket in buckets_response['Buckets']:
            if 'websitebucket' in bucket['Name']:
                bucket_name = bucket['Name']
                break

        if bucket_name:
            # Prepare config.json data
            config_data = {'API_URL': api_url}
            config_path = 'config.json'

            # Write the config file locally
            with open(config_path, 'w') as config_file:
                json.dump(config_data, config_file)

            print(f"✅ API URL written to {config_path}: {api_url}")

            # Upload config.json to S3 bucket
            s3.upload_file(config_path, bucket_name, 'config.json')
            print(f"✅ config.json uploaded to S3 bucket: {bucket_name}")

        else:
            print("❌ No S3 bucket found with 'websitebucket' in its name.")
    else:
        print("❌ API URL output not found in stack.")

except boto3.exceptions.S3UploadFailedError as e:
    print(f"🚨 S3 Upload Error: {e}")
except Exception as e:
    print(f"🚨 An error occurred: {e}")
