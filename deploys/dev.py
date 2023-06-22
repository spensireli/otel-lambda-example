from aws_cdk import Environment, Stack
from constructs import Construct
from infrastructure import spenco


ACCOUNT_ID = '427331153417'
REGION = 'us-east-1'
ENVIRONMENT = Environment(account=ACCOUNT_ID, region=REGION)


class Deploy(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        self.api = spenco.ApiExample(self, id_='spenco')

