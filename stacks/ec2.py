from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    Stack,
    CfnOutput
)
import os

class ImageHostingStack(Stack):
    def __init__(
        self,
        scope: Stack,
        id: str,
        vpc: ec2.IVpc,
        iam_role: iam.IRole,
        website_bucket: s3.IBucket,
        db_endpoint: str,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        
        self.vpc = vpc
        self.role = iam_role
        self.website_bucket = website_bucket

        # Create a dedicated assets directory to avoid long path issues
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Copy just the index.html to the assets directory
        index_html_src = os.path.join(os.path.dirname(__file__), "..", "index.html")
        index_html_dst = os.path.join(assets_dir, "index.html")
        
        if os.path.exists(index_html_src):
            import shutil
            shutil.copy2(index_html_src, index_html_dst)
        
        # Deploy only the index.html file to S3
        s3_deploy.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3_deploy.Source.asset(assets_dir)],
            destination_bucket=self.website_bucket,
            extract=False,
            retain_on_delete=False
        )

        # Create Security Group
        security_group = ec2.SecurityGroup(
            self, "WebServerSecurityGroup",
            vpc=self.vpc,
            description="Allow HTTP access to EC2",
            allow_all_outbound=True
        )

        # Allow HTTP (Port 80) Inbound Traffic
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic"
        )

        # Allow SSH (Port 22) Inbound Traffic
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allow SSH traffic from all IPs"
        )

        # Create EC2 instance
        web_server = ec2.Instance(
            self, "WebServer",
            instance_type=ec2.InstanceType("t2.micro"),  # Free tier eligible
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group,
            role=self.role,
            detailed_monitoring=False  # Disable detailed monitoring to stay in free tier
        )

        # Grant permissions to access the website bucket
        self.website_bucket.grant_read_write(web_server)

        # Define Flask app code that redirects to S3
        flask_app_code = """from flask import Flask, redirect
import os

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("http://YOUR_BUCKET_WEBSITE_ENDPOINT", code=302)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
"""

        user_data_script = f"""#!/bin/bash
# Update and install dependencies
yum update -y
yum install -y python3-pip awscli
pip3 install flask boto3

# Create directory structure
mkdir -p /home/ec2-user/app

# Create Flask app that redirects to S3
cat > /home/ec2-user/app/app.py << 'EOF'
{flask_app_code.replace("YOUR_BUCKET_WEBSITE_ENDPOINT", self.website_bucket.bucket_website_domain_name)}
EOF

# Create gunicorn start script
cat > /home/ec2-user/app/start_server.sh << 'EOS'
#!/bin/bash
source /home/ec2-user/.bashrc
cd /home/ec2-user/app
gunicorn -b 0.0.0.0:80 --access-logfile - --error-logfile - app:app
EOS

chmod +x /home/ec2-user/app/start_server.sh

# Create systemd service file
cat > /tmp/flaskapp.service << 'EOS'
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/app
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ec2-user/app/start_server.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOS

# Move service file to correct location and enable
sudo mv /tmp/flaskapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable flaskapp
sudo systemctl start flaskapp

# Verify service is running
sleep 5
sudo systemctl status flaskapp --no-pager

# Check if app is listening on port 80
sudo netstat -tulnp | grep 80
"""

        web_server.add_user_data(user_data_script)

        # Output the public IP and website URL
        CfnOutput(
            self, "InstancePublicIp",
            value=web_server.instance_public_ip,
            description="Public IP address of the EC2 instance"
        )
        
        CfnOutput(
            self, "WebsiteURL",
            value=self.website_bucket.bucket_website_url,
            description="URL of the S3 hosted website"
        )