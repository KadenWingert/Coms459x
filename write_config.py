import boto3
import json

# Ensure to use the session correctly for both profile and region
session = boto3.Session(profile_name='kadenwin', region_name='us-east-2')
cloudformation = session.client('cloudformation')
s3 = session.client('s3')  # Create S3 client

stack_name = 'ImageStorageS3Stack'  # Make sure this is the correct stack name as per your AWS console

try:
    # Fetch stack outputs
    response = cloudformation.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']

    # Initialize variables to store API URL
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
            config_data = {
                'API_URL': api_url
            }
            config_path = 'config.json'  # Update local path to 'config.json'

            # Write the config file locally
            with open(config_path, 'w') as config_file:
                json.dump(config_data, config_file)

            print(f"API URL written to {config_path}: {api_url}")

            # Upload the config.json to the root of the S3 bucket, not with the full path
            s3.upload_file(config_path, bucket_name, 'config.json')  # Only the file name in the S3 path

            print(f"config.json uploaded to S3 bucket: {bucket_name}")
        else:
            print("No S3 bucket found with 'websitebucket' in its name.")
    else:
        print("API URL output not found in stack.")
except boto3.exceptions.S3UploadFailedError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
