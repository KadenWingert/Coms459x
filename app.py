#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.vpc import VpcStack
from stacks.s3 import S3Stack
from stacks.iam import IamStack
from stacks.rds import RdsStack
from stacks.ec2 import ImageHostingStack

app = App()

# Define environment
env = Environment(account="945839052165", region="us-east-2")

# Create foundational stacks
vpc_stack = VpcStack(app, "VpcStack", env=env)
s3_stack = S3Stack(app, "S3Stack", env=env)
iam_stack = IamStack(app, "IamStack", env=env)
rds_stack = RdsStack(app, "RdsStack", vpc=vpc_stack.vpc, env=env)

# Create main stack
ImageHostingStack(
    app, 
    "ImageHostingStack",
    vpc=vpc_stack.vpc,
    s3_bucket=s3_stack.bucket,
    iam_role=iam_stack.role,
    db_endpoint=rds_stack.db.db_instance_endpoint_address,
    env=env
)

app.synth()