#!/usr/bin/env python3

import os
from aws_cdk import core

from stacks.workshop_stack import CdkWorkshopStack
from stacks.fargate import MyFargateStack
from stacks.sftp import SFTPIntegrationStack
from stacks.pipeline import PipelineStack

app = core.App()

CdkWorkshopStack(app, "workshop", env={'region': 'us-west-2'})

MyFargateStack(app, "fargate", env={
    'region': 'ap-southeast-2',
    'account': os.environ['CDK_DEFAULT_ACCOUNT'],
})

SFTPIntegrationStack(app, "sftp", env={
    'region': 'ap-southeast-2',
    'account': os.environ['CDK_DEFAULT_ACCOUNT'],
})

PipelineStack(app, "pipeline")

app.synth()
