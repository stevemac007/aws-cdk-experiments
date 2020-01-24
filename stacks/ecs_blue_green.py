from aws_cdk import core

from aws_cdk import (
    aws_ec2 as ec2,
    aws_route53_targets as target,
    aws_route53 as r53,
    aws_ecs as ecs,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_cloudwatch as cloudwatch,
    aws_certificatemanager as certmgr,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elb2)


class ECSBlueGreenStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain_name, domain_zone_name, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # // Network infrastructure
        vpc = ec2.Vpc(self, 'VPC', max_azs=2)
        serviceSG = ec2.SecurityGroup(self, 'ServiceSecurityGroup', vpc=vpc)

        # // Lookup pre-existing TLS certificate
        certificateArn = ssm.StringParameter.from_string_parameter_attributes(self,
                                                                              'CertArnParameter',
                                                                              parameter_name='CertificateArn-'+domain_name).string_value

        # # // Load balancer
        # load_balancer = elb2.ApplicationLoadBalancer(self,
        #                                              'ServiceLB',
        #                                              vpc=vpc,
        #                                              internet_facing=True)
        #
        # serviceSG.connections.allow_from(load_balancer, ec2.Port.tcp(80))
        #
        domain_zone = r53.HostedZone.from_lookup(self, 'Zone',
                                                 domain_name=domain_zone_name)
        #
        # r53_record = r53.ARecord(self, "DNS",
        #                          zone=domain_zone,
        #                          record_name=domain_name,
        #                          target=r53.RecordTarget.from_alias(target.LoadBalancerTarget(load_balancer)))

        # # // Primary traffic listener
        # listener = load_balancer.add_listener('PublicListenerrr',
        #                                       port=443,
        #                                       open=True,
        #                                       certificate_arns=[certificateArn])

        # # // Second listener for test traffic
        # test_listener = load_balancer.add_listener('TestListenerrr',
        #                                            port=9002,
        #                                            protocol=elb2.ApplicationProtocol.HTTPS,
        #                                            certificate_arns=[certificateArn])
        #
        # # // First target group for blue fleet
        # tg1 = listener.add_targets('ECS',
        #                            port=80,
        #                            deregistration_delay=core.Duration.seconds(30),
        #                            targets=[
        #
        #                            ],
        #                            health_check=elb2.HealthCheck(interval=core.Duration.seconds(5),
        #                                                          healthy_http_codes='200',
        #                                                          healthy_threshold_count=2,
        #                                                          unhealthy_threshold_count=3,
        #                                                          timeout=core.Duration.seconds(4)))
        #
        # # // Second target group for green fleet
        # tg2 = test_listener.add_targets('ECS2',
        #                                 port=80,
        #                                 deregistration_delay=core.Duration.seconds(30),
        #                                 targets=[
        #
        #                                 ],
        #                                 health_check=elb2.HealthCheck(interval=core.Duration.seconds(5),
        #                                                               healthy_http_codes='200',
        #                                                               healthy_threshold_count=2,
        #                                                               unhealthy_threshold_count=3,
        #                                                               timeout=core.Duration.seconds(4)))
        #
        # # // Alarms: monitor 500s and unhealthy hosts on target groups
        # cloudwatch.Alarm(self, 'TargetGroupUnhealthyHosts',
        #                  metric=tg1.metric_unhealthy_host_count(),
        #                  threshold=1,
        #                  evaluation_periods=2
        #                  )
        #
        # cloudwatch.Alarm(self, 'TargetGroup5xx',
        #                  metric=tg1.metric_http_code_target(code=elb2.HttpCodeTarget.TARGET_5XX_COUNT),
        #                  threshold=1,
        #                  evaluation_periods=1,
        #                  period=core.Duration.minutes(1)
        #                  )
        #
        # cloudwatch.Alarm(self, 'TargetGroup2UnhealthyHosts',
        #                  metric=tg2.metric_unhealthy_host_count(),
        #                  threshold=1,
        #                  evaluation_periods=2
        #                  )
        #
        # cloudwatch.Alarm(self, 'TargetGroup25xx',
        #                  metric=tg2.metric_http_code_target(code=elb2.HttpCodeTarget.TARGET_5XX_COUNT),
        #                  threshold=1,
        #                  evaluation_periods=1,
        #                  period=core.Duration.minutes(1)
        #                  )


        # // Roles
        iam.Role(self, 'ServiceTaskDefExecutionRole',
                 assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
                 managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonECSTaskExecutionRolePolicy') ]
                 )

        iam.Role(self, 'ServiceTaskDefTaskRole',
                 assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
                 )

        iam.Role(self, 'CodeDeployRole',
                 assumed_by=iam.ServicePrincipal('codedeploy.amazonaws.com'),
                 managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('AWSCodeDeployRoleForECS') ]
                 )

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        obj = ecs_patterns.ApplicationLoadBalancedFargateService(self, "MyFargateService",
                                                                 cluster=cluster,            # Required
                                                                 cpu=512,                    # Default is 256
                                                                 desired_count=2,            # Default is 1
                                                                 # load_balancer=load_balancer,
                                                                 domain_name=domain_name,
                                                                 domain_zone=domain_zone,
                                                                 certificate=certmgr.Certificate.from_certificate_arn(self, "Cert", certificate_arn=certificateArn),
                                                                 # protocol=elb2.ApplicationProtocol.HTTPS,
                                                                 task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                                     image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")),
                                                                 memory_limit_mib=2048      # Default is 512
                                                                 )

        # obj.node.add_override("Properties.DeploymentController", "CODE_DEPLOY")

        test_listener = obj.load_balancer.add_listener('TestListenerrr',
                                                       port=9002,
                                                       protocol=elb2.ApplicationProtocol.HTTPS,
                                                       certificate_arns=[certificateArn])

        # // Second target group for green fleet
        tg2 = test_listener.add_targets('ECS2',
                                        port=80,
                                        deregistration_delay=core.Duration.seconds(30),
                                        targets=[

                                        ],
                                        health_check=elb2.HealthCheck(interval=core.Duration.seconds(5),
                                                                      healthy_http_codes='200',
                                                                      healthy_threshold_count=2,
                                                                      unhealthy_threshold_count=3,
                                                                      timeout=core.Duration.seconds(4)))

        # core.CfnOutput(self,
        #                "DNSEndpoint",
        #                value="https://"+r53_record.domain_name)
