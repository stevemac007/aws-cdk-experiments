from aws_cdk import (core, aws_codebuild as codebuild,
                     aws_codecommit as codecommit,
                     aws_codepipeline as codepipeline,
                     aws_codepipeline_actions as codepipeline_actions,
                     aws_codedeploy as codedeploy,
                     aws_iam as iam,
                     aws_lambda as lambda_, aws_s3 as s3,
                     aws_ecr as ecr)


class PipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        code = codecommit.Repository.from_repository_name(self, "ImportedRepo", "smac-cdk-test")

        sourceOutput = codepipeline.Artifact("Output")

        sourceAction = codepipeline_actions.CodeCommitSourceAction(action_name="Source",
                                                                   repository=code,
                                                                   output=sourceOutput)

        # baseImageRepo = ecr.Repository.from_repository_name(self, 'BaseRepo', 'reinvent-trivia-backend-base');
        # baseImageOutput = codepipeline.Artifact('BaseImage')
        #
        # dockerImageSourceAction = codepipeline_actions.EcrSourceAction(
        #   action_name= 'BaseImage',
        #   repository= baseImageRepo,
        #   image_tag= 'release',
        #   output=baseImageOutput,
        # )

        cdk_build = codebuild.PipelineProject(self, "CdkBuild",
                                              project_name="smac-cdk-example-build",
                                              # timeout=Duration(15 min),
                        build_spec=codebuild.BuildSpec.from_object(dict(
                            version="0.2",
                            phases=dict(
                                install=dict(
                                    commands=[
                                        "make init",
                                        "make requirements"
                                    ]
                                ),
                                build=dict(commands=[
                                    "make lint",
                                    "make diff-test",
                                    "make deploy-test"])),
                            artifacts={
                                "base-directory": "cdk.out",
                                "files": [
                                    "*.json"]},
                            environment=dict(buildImage=
                                codebuild.LinuxBuildImage.UBUNTU_14_04_PYTHON_3_7_1))))

        cdk_build.add_to_role_policy(iam.PolicyStatement(
                actions=["route53:ListHostedZonesByName"],
                resources=["*"],
        ))

        buildAction = codepipeline_actions.CodeBuildAction(action_name="Build",
                                                           input=sourceOutput,
                                                           project=cdk_build)

        pipeline = codepipeline.Pipeline(self,
                                         'Pipeline',
                                         pipeline_name='smac-cdk-example-pipeline',
                                         stages=[
                                             codepipeline.StageProps(stage_name="Build",
                                                                     actions=[sourceAction,
                                                                              ]),
                                             codepipeline.StageProps(stage_name="DeployDev",
                                                                     actions=[buildAction])
                                         ])

        core.Tag.add(self, 'Owner', 'stevemac')
