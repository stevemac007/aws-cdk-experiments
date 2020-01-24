from aws_cdk import core

from aws_cdk import (
    aws_ec2 as ec2,
    )


class MyVPCStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)     # default is all AZs in region
