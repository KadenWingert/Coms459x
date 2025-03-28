from aws_cdk import (
    aws_iam as iam,
    Stack,
    RemovalPolicy,
    PhysicalName
)

class IamStack(Stack):
    def __init__(self, scope: Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.role = iam.Role(
            self, "WebServerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            # Either use an explicit name:
            role_name=f"WebServerRole-{self.stack_name}",
            # Or let CDK generate one:
            # role_name=PhysicalName.GENERATE_IF_NEEDED,
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRDSFullAccess")
            ]
        )