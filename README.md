# How to run the CDK

## Prerequisites
1. You must have the aws cli installed. For instructions on how to do so, visit this link: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. Create a secret access key for your user in the aws console and save both the secret key and the secret access key for later
3. Install the aws cli plugin in vscode, intellij, or whwatever IDE you are using
4. Go to the plugin you just installed and click "connect to AWS" and click "add new connection". Then click "IAM credentials" and enter in your user name, access key, and secret access key
5. Now you should be able to run aws commands. If you made this account the default profile, you can run the commands normally. If you named your profile somethign else, ex: mark, then instead of running a command that starts with 'cdk' such as cdk deploy, you would run cdk deploy --profile mark

##  1. Set up the environment
```python3 -m venv .venv```     # Create virtual environment
``` source .venv/bin/activate ```   # Activate it (Linux/Mac)
 or .venv\Scripts\activate.bat (Windows)
``` pip install -r requirements.txt ```

## 2. Bootstrap your AWS account (first time only):
cdk bootstrap aws://945839052165/us-east-2

## 3. Deploy the stack
``` cdk deploy --all ```
If you want to avoid the messages asking for your apporval to provision certain resources, run `cdk deploy --all --require-approval never`

## 4. Destroy the stack
To save costs, destroy the stack after it is created by running
``` cdk destroy ```