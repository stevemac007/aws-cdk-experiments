import unittest

from aws_cdk import core

from stacks.workshop_stack import CdkWorkshopStack
from stacks.fargate import MyFargateStack


class TestCdkWorkshopStack(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = core.Stack(self.app, "TestStack")
