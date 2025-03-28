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

        # 1. Create S3 Bucket
        self.image_bucket = s3.Bucket(
            self, "ImageStorageBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[
                s3.CorsRule(
                    allowed_origins=["*"],
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
                        s3.HttpMethods.DELETE
                    ],
                    allowed_headers=["*"],
                    max_age=300
                )
            ]
        )

        # 2. Create Lambda Function
        lambda_function = _lambda.Function(
            self, "ImageHandlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": self.image_bucket.bucket_name,
            }
        )
        self.image_bucket.grant_read_write(lambda_function)

        # 3. Create API Gateway
        api = apigateway.RestApi(
            self, "ImageApiGateway",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
                allow_credentials=False
            )
        )


        # 4. Add Lambda integration with proper method responses
        method_response = apigateway.MethodResponse(
            status_code="200",
            response_parameters={
                "method.response.header.Access-Control-Allow-Origin": True
            }
        )

        lambda_integration = apigateway.LambdaIntegration(
    lambda_function,
    proxy=True  # ✅ Use proxy integration to handle CORS in Lambda
)

        images = api.root.add_resource("images")

        images.add_method("POST", lambda_integration)
        images.add_method("GET", lambda_integration)
        images.add_method("DELETE", lambda_integration)

        # 6. Add permission for API Gateway to invoke Lambda
        # (This must come AFTER api is defined)
        lambda_function.add_permission(
            "ApiGatewayPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api.arn_for_execute_api()
        )

        # 7. Output the API URL
        self.api_url = CfnOutput(self, "ApiUrl", value=api.url)