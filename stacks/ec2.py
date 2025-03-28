from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
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
        s3_bucket: s3.IBucket,
        iam_role: iam.IRole,
        db_endpoint: str,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        
        self.vpc = vpc
        self.bucket = s3_bucket
        self.role = iam_role

        # Create asset for the index.html file
        index_html_asset = s3_assets.Asset(
            self, "IndexHtmlAsset",
            path=os.path.join(os.path.dirname(__file__), "..", "index.html")
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
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group,
            role=self.role,
            detailed_monitoring=True
        )

        # Grant permissions
        self.bucket.grant_read_write(web_server)

        # Define Flask app code
        flask_app_code = """from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def index():
    try:
        if not os.path.exists(os.path.join(app.template_folder, 'index.html')):
            return "Template not found at: " + os.path.join(app.template_folder, 'index.html'), 500
        return render_template("index.html")
    except Exception as e:
        return "Error: {}".format(str(e)), 500
"""

        user_data_script = f"""#!/bin/bash
# Update and install dependencies
yum update -y
yum install -y python3-pip awscli
pip3 install flask boto3 pymysql gunicorn

# Create directory structure
mkdir -p /home/ec2-user/app/templates

# Download index.html from S3
aws s3 cp s3://{index_html_asset.s3_bucket_name}/{index_html_asset.s3_object_key} /home/ec2-user/app/templates/index.html

# Create Flask app
cat > /home/ec2-user/app/app.py << 'EOF'
{flask_app_code}
EOF

# Set proper permissions
chown -R ec2-user:ec2-user /home/ec2-user/app
chmod 755 /home/ec2-user/app
chmod 644 /home/ec2-user/app/templates/index.html

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
        
        # Grant the instance permission to read the asset
        index_html_asset.grant_read(iam_role)

        # Output the public IP for easy access
        CfnOutput(
            self, "InstancePublicIp",
            value=web_server.instance_public_ip,
            description="Public IP address of the EC2 instance"
        )