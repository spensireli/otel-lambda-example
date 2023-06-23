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


        self.hello_world_role = iam.Role(
                    self, "hello-world-role",
                    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                    description='Hello World Lambda Role',
                    managed_policies=[
                        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaVPCAccessExecutionRole'),
                    ]
                )


        self.lambda_function_variables = {
            'AWS_LAMBDA_EXEC_WRAPPER': '/opt/otel-instrument',
            'OPENTELEMETRY_COLLECTOR_CONFIG_FILE': '/var/task/config.yaml'
        }


        self.policy = iam.Policy(
            self, "policy",
            statements=[
                iam.PolicyStatement(
                    sid='AssumeRolePermissions',
                    actions=['sts:AssumeRole'],
                    resources=[f'arn:aws:iam::*:role/dataplane-{id_.replace("_", "-")}']
                ),
                iam.PolicyStatement(
                    sid='XrayPermissions',
                    actions=["logs:PutLogEvents",
                             "logs:CreateLogGroup",
                             "logs:CreateLogStream",
                             "logs:DescribeLogStreams",
                             "logs:DescribeLogGroups",
                             "logs:PutRetentionPolicy",
                             "xray:PutTraceSegments",
                             "xray:PutTelemetryRecords",
                             "xray:GetSamplingRules",
                             "xray:GetSamplingTargets",
                             "xray:GetSamplingStatisticSummaries",
                             "ssm:GetParameters"],
                    resources=['*']
                )
            ]
        )
        self.policy.attach_to_role(self.hello_world_role)


        self.function = aws_lambda.Function(
            self, "function",
            function_name=f'hello-{id_.replace("_", "-")}',
            runtime=cast(aws_lambda.Runtime, aws_lambda.Runtime.PYTHON_3_9),
            handler=f'lib.lambda_code.{id_}.{id_}.lambda_handler',
            code=aws_lambda.Code.from_asset(f'./build/{id_}.zip'),
            role=self.hello_world_role,
            layers=[aws_lambda.LayerVersion.from_layer_version_arn(
                self, 'adot-layer',
                Fn.sub(body='arn:aws:lambda:${AWS::Region}:901920570463:layer:aws-otel-python-amd64-ver-1-17-0:1')
            )],
            tracing=aws_lambda.Tracing.ACTIVE,
            environment=self.lambda_function_variables,
            environment_encryption=self.encryption_key,
            timeout=Duration.seconds(900),
            retry_attempts=0,
        )

        self.function_integration = apigateway.LambdaIntegration(self.function)
        self.hello_world_api = self.rest_api.root.add_resource("hello")
        self.hello_world_api.add_method(http_method="GET", integration=self.function_integration)

        self.sleepy_api = self.rest_api.root.add_resource("sleepy")
        self.sleepy_api.add_method(http_method="GET", integration=self.function_integration)

        self.broken_api = self.rest_api.root.add_resource("broken")
        self.broken_api.add_method(http_method="GET", integration=self.function_integration)
