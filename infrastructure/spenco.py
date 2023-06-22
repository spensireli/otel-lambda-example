from aws_cdk import (aws_apigateway as apigateway, Duration, aws_ec2 as ec2,
                     aws_iam as iam, aws_kms as kms, aws_lambda, aws_logs as logs, aws_wafv2 as wafv2, Fn, Tags)
from constructs import Construct
from typing import cast

class ApiExample(Construct):
    def __init__(self, scope: Construct, id_: str):
        super().__init__(scope, id_)
        self.encryption_key = kms.Key(self, 'spenco-api-kms-key', enable_key_rotation=True)
        self.log_group = logs.LogGroup(self, "spenco-api-logs")

        self.rest_api = apigateway.RestApi(
            self, "spencoapi",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                max_age=Duration.days(0)
        ),
            deploy_options=apigateway.StageOptions(
                access_log_destination=apigateway.LogGroupLogDestination(self.log_group),
                access_log_format=apigateway.AccessLogFormat.json_with_standard_fields(
                    caller=True,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True
                ),
                logging_level=apigateway.MethodLoggingLevel.INFO
            )
        )
