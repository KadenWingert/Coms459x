# deploy_and_generate_config.sh

cdk deploy --all --require-approval never --profile kadenwin
python ../write_config.py
