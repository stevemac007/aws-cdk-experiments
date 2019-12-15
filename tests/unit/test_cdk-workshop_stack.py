import unittest

from aws_cdk import core

from hello.hello_construct import HelloConstruct

class TestCdkWorkshopStack(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = core.Stack(self.app, "TestStack")