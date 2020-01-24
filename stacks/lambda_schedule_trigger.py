from aws_cdk import core

from aws_cdk import (
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_ssm as ssm)


class MyFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambdaFn = lambda_.Function(
            self, "Singleton",
            code=lambda_.Code.asset('lambda'),
            handler="index.main",
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
        )

        api_key_ssm = ssm.StringParameter(self,
                                          parameter_name="/lambda/WorkflowMaxTimesheetBot/API_KEY",
                                          string_value="changeme")

        account_key_ssm = ssm.StringParameter(self,
                                              parameter_name="/lambda/WorkflowMaxTimesheetBot/ACCOUNT_KEY",
                                              string_value="changeme")

        lambdaFn.add_environment("SSM_API_KEY", api_key_ssm.parameter_name)
        lambdaFn.add_environment("SSM_ACCOUNT_KEY", account_key_ssm.parameter_name)

        api_key_ssm.grant_read(lambdaFn)
        account_key_ssm.grant_read(lambdaFn)

        # Run every day at 6PM UTC
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='0',
                hour='18',
                month='*',
                week_day='MON-FRI',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))
