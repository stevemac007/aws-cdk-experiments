#    "deploy-test-infra": "tsc && cdk deploy --app 'node infra-setup.js' --require-approval never TriviaBackendTest",
#    "deploy-prod-infra": "tsc && cdk deploy --app 'node infra-setup.js' --require-approval never TriviaBackendProd"

init:
	npm install -g aws-cdk
	cdk --version

lint:
	cdk synth


requirements:
	pip install -r requirements.txt

run-dockerfile:
	docker run -P -d nginxdemos/hello

build-all:
	cdk deploy --require-approval never sftp
	cdk deploy --require-approval never fargate
	cdk deploy --require-approval never pipeline

deploy-test:
	cdk deploy --require-approval never TriviaBackendTest

diff-test:
	cdk diff --require-approval never TriviaBackendTest

destroy:
	cdk destroy -f sftp
	cdk destroy -f fargate
	cdk destroy -f workshop
	cdk destroy -f pipeline
	cdk destroy -f TriviaBackendTest
	cdk destroy -f TriviaBackendProd
