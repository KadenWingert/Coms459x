#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.vpc import VpcStack
from stacks.s3 import ImageStorageS3Stack
from stacks.website import WebsiteS3Stack
from stacks.iam import IamStack
from stacks.rds import RdsStack
from stacks.ec2 import ImageHostingStack
app = App()

# Define environment
env = Environment(account="945839052165", region="us-east-2")

# Create foundational stacks
vpc_stack = VpcStack(app, "VpcStack", env=env)
website_s3_stack = WebsiteS3Stack(app, "WebsiteS3Stack", env=env)  # Website Hosting Bucket
image_s3_stack = ImageStorageS3Stack(app, "ImageStorageS3Stack", env=env)  # Image Storage Bucket
iam_stack = IamStack(app, "IamStack", env=env)
rds_stack = RdsStack(app, "RdsStack", vpc=vpc_stack.vpc, env=env)

# Create main stack
ImageHostingStack(
    app, 
    "ImageHostingStack",
    vpc=vpc_stack.vpc,
    iam_role=iam_stack.role,
    website_bucket=website_s3_stack.website_bucket,  # ✅ Now using correct website bucket!
    db_endpoint=rds_stack.db.db_instance_endpoint_address,
    env=env
)

app.synth()
