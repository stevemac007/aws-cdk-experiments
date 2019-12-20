from aws_cdk import core

from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_route53_targets as target,
    aws_route53 as r53,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_transfer as transfer)


class SFTPIntegrationStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        sftp_server = transfer.CfnServer(self,
                                         "SFTPServer",
                                         endpoint_type="PUBLIC",
                                         )

        sftp_bucket = s3.Bucket(self, "SFTPBucket")

        sftp_role = iam.Role(self,
                             "S3AccessRole",
                             assumed_by=iam.ServicePrincipal("transfer.amazonaws.com"))

        sftp_role.add_to_policy(iam.PolicyStatement(actions=[
                                                        "s3:ListBucket"
                                                    ],
                                                    resources=[
                                                        sftp_bucket.bucket_arn
                                                    ],
                                                    # conditions=[]
                                                    )
                                )

        sftp_role.add_to_policy(iam.PolicyStatement(actions=[
                                                        "s3:PutObject",
                                                        "s3:GetObject",
                                                        "s3:DeleteObjectVersion",
                                                        "s3:DeleteObject",
                                                        "s3:GetObjectVersion"
                                                    ],
                                                    resources=[
                                                        sftp_bucket.bucket_arn+"/*"
                                                    ]))

        incoming_user = transfer.CfnUser(self,
                                         "InboundUser",
                                         server_id=sftp_server.attr_server_id,
                                         user_name="incoming",
                                         home_directory="/"+sftp_bucket.bucket_name+"/sftp/incoming/",
                                         ssh_public_keys=["ssh-rsa blart/bling/bloop/blift/blart+blart/8hEfbls49Faf+blart steve@blart.com"],
                                         role=sftp_role.role_arn)

        outbound_user = transfer.CfnUser(self,
                                         "OutboundUser",
                                         server_id=sftp_server.attr_server_id,
                                         user_name="outgoing",
                                         home_directory="/"+sftp_bucket.bucket_name+"/sftp/outgoing/",
                                         ssh_public_keys=["ssh-rsa blart/bling/bloop/blift/blart+blart/8hEfbls49Faf+blart steve@blart.com"],
                                         role=sftp_role.role_arn)

        core.CfnOutput(self, "SFTP Server", value=sftp_server.attr_server_id)

        zone = r53.HostedZone.from_lookup(self, "Zone", domain_name="thanatopho.be")  # thanatopho.be

        dns = r53.RecordSet(self,  "SFTPRecordeSet",
                            record_type=r53.RecordType.CNAME,
                            record_name="sftp",
                            zone=zone,
                            target=r53.RecordTarget.from_values(sftp_server.attr_server_id+".server.transfer."+self.region+".amazonaws.com"))

        core.Tag.add(self, 'Owner', 'stevemac')
