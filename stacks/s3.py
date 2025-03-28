from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Stack,
    CfnOutput,
    PhysicalName,
    RemovalPolicy,
    Duration
)

class ImageStorageS3Stack(Stack):
    def __init__(self, scope: Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Create an S3 Bucket for image storage
        self.image_bucket = s3.Bucket(
            self, "ImageStorageBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                    expiration=Duration.days(30)
                )
            ],
            # CORS configuration for the entire bucket
            cors=[
                s3.CorsRule(
                    allowed_origins=["*"],  # Allow any origin
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.DELETE],
                    allowed_headers=["*"],  # Allow all headers, or specify if needed
                    max_age=300  # Just use an integer value for max_age (in seconds)
                )
            ]
        )

        # 2. Lambda Function to interact with S3
        lambda_function = _lambda.Function(
            self, "ImageHandlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),  # Path to your Lambda code folder
            environment={
                "BUCKET_NAME": self.image_bucket.bucket_name,
            }
        )

        # 3. Grant Lambda function access to the S3 bucket
        self.image_bucket.grant_read_write(lambda_function)

        # 4. Create the API Gateway to interact with Lambda
        api = apigateway.LambdaRestApi(
            self, "ImageApiGateway",
            handler=lambda_function
        )

        # Define a resource and methods for uploading, retrieving, and deleting images
        images = api.root.add_resource("images")
        images.add_method("POST")  # POST /images -> Lambda to upload an image
        images.add_method("GET")   # GET /images -> Lambda to retrieve an image
        images.add_method("DELETE")  # DELETE /images -> Lambda to delete an image

        # Enable CORS on the /images resource
        images.add_cors_preflight(
            allow_origins=["*"],  # You can specify your frontend URL here, or use "*" for all
            allow_methods=["GET", "POST", "DELETE"],  # Allow methods
            allow_headers=["Content-Type"],  # Allow necessary headers
            max_age=Duration.seconds(300)  # Use Duration.seconds() to convert seconds to Duration
        )


        # Expose the API URL as an output
        self.api_url = CfnOutput(self, "ApiUrl", value=api.url)  # Correctly create the output
