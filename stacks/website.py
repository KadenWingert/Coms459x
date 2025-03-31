import subprocess
import os
import json
from aws_cdk import aws_s3 as s3, aws_s3_deployment as s3_deploy, Stack, RemovalPolicy

class WebsiteS3Stack(Stack):
    def __init__(self, scope: Stack, id: str, api_url: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define paths
        project_root = os.path.join(os.path.dirname(__file__), "..")
        website_assets_dir = os.path.join(project_root, "website_assets")
        build_dir = os.path.join(website_assets_dir, "build")  # Path where React build output is stored

        # Run npm build
        print("🚀 Running npm install and npm run build...")
        subprocess.run(["npm", "install"], cwd=website_assets_dir, check=True)  # Ensure dependencies are installed
        subprocess.run(["npm", "run", "build"], cwd=website_assets_dir, check=True)  # Build React app

        # Create S3 bucket for hosting
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

        # Deploy the built website to S3
        s3_deploy.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3_deploy.Source.asset(build_dir)],  # Upload built React app
            destination_bucket=self.website_bucket
        )

