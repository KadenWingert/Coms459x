from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    Stack,
    RemovalPolicy
)
import os

class WebsiteS3Stack(Stack):
    def __init__(self, scope: Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket for website hosting
        self.website_bucket = s3.Bucket(
            self, "WebsiteBucket",
            website_index_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                ignore_public_acls=False,
                block_public_policy=False,
                restrict_public_buckets=False
            )
        )

        # Get absolute path to 'website_assets/' directory
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "website_assets")

        # Deploy entire folder to S3
        s3_deploy.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3_deploy.Source.asset(assets_dir)],  # ✅ Now using a directory
            destination_bucket=self.website_bucket
        )
