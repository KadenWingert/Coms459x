from aws_cdk import aws_ec2 as ec2, Stack

class VpcStack(Stack):
    def __init__(self, scope: Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # Use the default VPC (which already has subnets in multiple AZs)
        self.vpc = ec2.Vpc.from_lookup(
            self, "DefaultVPC",
            is_default=True
        )