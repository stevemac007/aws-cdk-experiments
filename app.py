#!/usr/bin/env python3

import os
from aws_cdk import core

from stacks.workshop_stack import CdkWorkshopStack
from stacks.fargate import MyFargateStack
from stacks.sftp import SFTPIntegrationStack
from stacks.pipeline import PipelineStack
from stacks.ecs_blue_green import ECSBlueGreenStack
from stacks.vpc import MyVPCStack

app = core.App()

MyVPCStack(app, "VPC", env={'region': 'us-west-2'})

# CdkWorkshopStack(app, "workshop", env={'region': 'us-west-2'})
#
# MyFargateStack(app, "fargate", env={
#     'region': 'ap-southeast-2',
#     'account': os.environ['CDK_DEFAULT_ACCOUNT'],
# })
#
# SFTPIntegrationStack(app, "sftp", env={
#     'region': 'ap-southeast-2',
#     'account': os.environ['CDK_DEFAULT_ACCOUNT'],
# })
#
# PipelineStack(app, "pipeline")
#

ECSBlueGreenStack(app, 'TriviaBackendTest',
                  domain_name='api-test.thanatopho.be',
                  domain_zone_name='thanatopho.be',
                  env={
                      'region': 'ap-southeast-2',
                      'account': os.environ['CDK_DEFAULT_ACCOUNT'],
                  })

ECSBlueGreenStack(app, 'TriviaBackendProd',
                  domain_name='api.thanatopho.be',
                  domain_zone_name='thanatopho.be',
                  env={
                      'region': 'ap-southeast-2',
                      'account': os.environ['CDK_DEFAULT_ACCOUNT'],
                  })

core.Tag.add(app, 'Owner', 'stevemac')

app.synth()
