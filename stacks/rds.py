from aws_cdk import aws_rds as rds, aws_ec2 as ec2, Stack, RemovalPolicy, Duration, CfnOutput

class RdsStack(Stack):
    def __init__(self, scope: Stack, id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create subnet group using public subnets from default VPC
        subnet_group = rds.SubnetGroup(
            self, "DBSubnetGroup",
            description="Subnet group for database",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create DB instance with t4g.micro and supported MySQL version
        self.db = rds.DatabaseInstance(
            self, "ImageMetadataDB",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_33  # Supported version for t4g
            ),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            subnet_group=subnet_group,
            publicly_accessible=True,
            allocated_storage=20,
            max_allocated_storage=20,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            multi_az=False,
            credentials=rds.Credentials.from_generated_secret("admin"),
            database_name="image_metadata",
            backup_retention=Duration.days(0),
            port=3306
        )

        CfnOutput(self, "RdsEndpoint", value=self.db.db_instance_endpoint_address)