from aws_cdk import core

from aws_cdk import (
    aws_ec2 as ec2,
    aws_route53_targets as target,
    aws_route53 as r53,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs)


class MyFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)     # default is all AZs in region

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        obj = ecs_patterns.ApplicationLoadBalancedFargateService(self, "MyFargateService",
                                                                 cluster=cluster,            # Required
                                                                 cpu=512,                    # Default is 256
                                                                 desired_count=2,            # Default is 1
                                                                 task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                                     image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")),
                                                                 memory_limit_mib=2048,      # Default is 512
                                                                 public_load_balancer=True)  # Default is Falsede

        zone = r53.HostedZone.from_lookup(self, "Zone", domain_name="thanatopho.be")  # thanatopho.be

        dns = r53.RecordSet(self,  "ALBRecordeSet",
                            record_type=r53.RecordType.CNAME,
                            record_name="smac",
                            zone=zone,
                            target=r53.RecordTarget.from_alias(target.LoadBalancerTarget(obj.load_balancer)))

        core.Tag.add(self, 'Owner', 'stevemac')
