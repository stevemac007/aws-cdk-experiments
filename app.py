#!/usr/bin/env python3

from aws_cdk import core

from cdk-workshop.cdk-workshop_stack import CdkWorkshopStack


app = core.App()
CdkWorkshopStack(app, "cdk-workshop", env={'region': 'us-west-2'})

app.synth()
