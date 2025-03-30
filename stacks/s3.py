from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Stack,
    CfnOutput,
    PhysicalName,
    RemovalPolicy,
    aws_kms as kms,
    Duration
)



class ImageStorageS3Stack(Stack):
    def __init__(self, scope: Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create single KMS CMK
        self.cmk = kms.Key(
            self, "ImageEncryptionKey",
            enable_key_rotation=True,
            description="Master key for generating image encryption keys",
            policy=self.create_kms_key_policy()
        )

        # 1. Create S3 Bucket
        self.image_bucket = s3.Bucket(
            self, "ImageStorageS3Stack",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=False,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.cmk,
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
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": self.image_bucket.bucket_name,
                "KMS_KEY_ARN": self.cmk.key_arn  # Make sure to add this
            },
            timeout=Duration.seconds(30)
            # Remove layers parameter
        )
        # Grant Lambda permissions
        self.image_bucket.grant_read_write(lambda_function)
        self.cmk.grant_encrypt_decrypt(lambda_function)


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
        apigateway.MethodResponse(
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

    def create_kms_key_policy(self):
            return iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        sid="AllowKMSAdministration",
                        effect=iam.Effect.ALLOW,
                        principals=[iam.AccountRootPrincipal()],
                        actions=["kms:*"],
                        resources=["*"]
                    ),
                    iam.PolicyStatement(
                        sid="AllowLambdaToUseKey",
                        effect=iam.Effect.ALLOW,
                        principals=[iam.ServicePrincipal("lambda.amazonaws.com")],
                        actions=[
                            "kms:GenerateDataKey",
                            "kms:Encrypt",
                            "kms:Decrypt",
                            "kms:DescribeKey"
                        ],
                        resources=["*"]
                    )
                ]
            )
