#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.vpc import VpcStack
from stacks.s3 import ImageStorageS3Stack
from stacks.website import WebsiteS3Stack
from stacks.iam import IamStack
from stacks.rds import RdsStack
app = App()

# Define environment
env = Environment(account="945839052165", region="us-east-2")

# Create foundational stacks
vpc_stack = VpcStack(app, "VpcStack", env=env)
website_s3_stack = WebsiteS3Stack(app, "WebsiteS3Stack", env=env)  # Website Hosting Bucket
image_s3_stack = ImageStorageS3Stack(app, "ImageStorageS3Stack", env=env)  # Image Storage Bucket
iam_stack = IamStack(app, "IamStack", env=env)
rds_stack = RdsStack(app, "RdsStack", vpc=vpc_stack.vpc, env=env)



app.synth()
