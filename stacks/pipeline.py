from aws_cdk import (core, aws_codebuild as codebuild,
                     aws_codecommit as codecommit,
                     aws_codepipeline as codepipeline,
                     aws_codepipeline_actions as codepipeline_actions,
                     aws_codedeploy as codedeploy,
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
                        build_spec=codebuild.BuildSpec.from_object(dict(
                            version="0.2",
                            phases=dict(
                                install=dict(
                                    commands="make init"),
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


        buildAction = codepipeline_actions.CodeBuildAction(action_name="Build",
                                                           input=sourceOutput,
                                                           project=cdk_build)

        pipeline = codepipeline.Pipeline(self,
                                         'Pipeline',
                                         pipeline_name='smac-ecs-cfn-deploy',
                                         stages=[
                                             codepipeline.StageProps(stage_name="Build",
                                                                     actions=[sourceAction,
                                                                              # dockerImageSourceAction
                                                                              ]),
                                             codepipeline.StageProps(stage_name="DeployDev",
                                                                     actions=[buildAction])
                                         ])

        # lambda_build = codebuild.PipelineProject(self, 'LambdaBuild',
        #                                          project_name="smac-cdk-example",
        #                 build_spec=codebuild.BuildSpec.from_object(dict(
        #                     version="0.2",
        #                     phases=dict(
        #                         install=dict(
        #                             commands=[
        #                                 "cd lambda",
        #                                 "npm install"]),
        #                         build=dict(
        #                             commands="npm run build")),
        #                     artifacts={
        #                         "base-directory": "lambda",
        #                         "files": [
        #                             "index.js",
        #                             "node_modules/**/*"]},
        #                     environment=dict(buildImage=
        #                         codebuild.LinuxBuildImage.UBUNTU_14_04_NODEJS_10_14_1))))
        #
        # source_output = codepipeline.Artifact()
        # cdk_build_output = codepipeline.Artifact("CdkBuildOutput")
        # lambda_build_output = codepipeline.Artifact("LambdaBuildOutput")
        #
        # lambda_location = lambda_build_output.s3_location
        #
        # codepipeline.Pipeline(self, "Pipeline",
        #     stages=[
        #         codepipeline.StageProps(stage_name="Source",
        #             actions=[
        #                 codepipeline_actions.CodeCommitSourceAction(
        #                     action_name="CodeCommit_Source",
        #                     repository=code,
        #                     output=source_output)]),
        #         codepipeline.StageProps(stage_name="Build",
        #             actions=[
        #                 codepipeline_actions.CodeBuildAction(
        #                     action_name="Lambda_Build",
        #                     project=lambda_build,
        #                     input=source_output,
        #                     outputs=[lambda_build_output]),
        #                 codepipeline_actions.CodeBuildAction(
        #                     action_name="CDK_Build",
        #                     project=cdk_build,
        #                     input=source_output,
        #                     outputs=[cdk_build_output])]),
        #         codepipeline.StageProps(stage_name="Deploy",
        #             actions=[
        #                 codepipeline_actions.CloudFormationCreateUpdateStackAction(
        #                     action_name="Lambda_CFN_Deploy",
        #                     template_path=cdk_build_output.at_path(
        #                         "LambdaStack.template.json"),
        #                     stack_name="LambdaDeploymentStack",
        #                     admin_permissions=True,
        #                     parameter_overrides=dict(
        #                         lambda_code.assign(
        #                             bucket_name=lambda_location.bucket_name,
        #                             object_key=lambda_location.object_key,
        #                             object_version=lambda_location.object_version)),
        #                     extra_inputs=[lambda_build_output])])
        #         ]
        #     )


        ecs_deploy = codedeploy.EcsApplication(self,
                                               "ECSDemoApplication",
                                               application_name="blart")

        # codedeploy.EcsDeploymentGroup(self, )

        codedeploy.EcsDeploymentGroup.from_ecs_deployment_group_attributes(pipeline,
                                                                           'CodeDeployDeploymentGroup',
                                                                           application=ecs_deploy,
                                                                           deployment_group_name="blarrt")


        core.Tag.add(self, 'Owner', 'stevemac')
