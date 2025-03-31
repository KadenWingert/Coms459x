from aws_cdk import App, Environment
from stacks.vpc import VpcStack
from stacks.s3 import ImageStorageS3Stack
from stacks.website import WebsiteS3Stack

app = App()

# Define environment
env = Environment(account="945839052165", region="us-east-1")

# Create foundational stacks
vpc_stack = VpcStack(app, "VpcStack", env=env)
image_s3_stack = ImageStorageS3Stack(app, "ImageStorageS3Stack", env=env)  # Image Storage Bucket

website_s3_stack = WebsiteS3Stack(app, "WebsiteS3Stack", api_url=image_s3_stack.api_url.value, env=env)  # Website Hosting Bucket

app.synth()
