# How to run the CDK

## Prerequisites
1. You must have the aws cli installed. For instructions on how to do so, visit this link: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. Create a secret access key for your user in the aws console and save both the secret key and the secret access key for later. This allows for authenticating AWS API requests
3. Install the aws cli plugin in vscode, intellij, or whwatever IDE you are using
4. Go to the plugin you just installed and click "connect to AWS" and click "add new connection". Then click "IAM credentials" and enter in your user name, access key, and secret access key
5. Now you should be able to run aws commands. If you made this account the default profile, you can run the commands normally. If you named your profile somethign else, ex: johnDoe, then instead of running a command that starts with 'cdk' such as cdk deploy, you would run cdk deploy --profile johnDoe

##  1. Set up the environment
```python3 -m venv .venv```     # Create virtual environment
``` source .venv/bin/activate ```   # Activate it (Linux/Mac)
 or .venv\Scripts\activate.bat (Windows)
``` pip install -r requirements.txt ```

## 2. Bootstrap your AWS account (first time only):
cdk bootstrap aws://945839052165/us-east-1

## 3. Deploy the stack
cdk ```deploy --all --require-approval never``` 

## 4. Upload the Correct Url for API Gatewway
AFTER the stack finishes deploying, run this script (which is located in the hom directory of this project) to upload the API Gateway URL to the config.json file: `write_config.py`


## 4. Destroy the stack
To save costs, destroy the stack after you are done working on it by running
``` cdk destroy --all  --force ```


# Frontend Development
Note that if you are ONLY doing changes on the frontend ui, can can cd to the website_assets directory and run `npm start` because the frontend is just a basic react app

# Other
Since we are using the AWS CDK, do NOT create/delete/modify resources from the console. Doing so will create what is called 'stack drift' and will mess things up, and can cause some headaches when trying to recreate/deploy the infrastructure.