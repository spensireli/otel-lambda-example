import json
from opentelemetry import trace
from opentelemetry import metrics


tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
success_counter = meter.create_counter(
    "success.counter", unit="1", description="Counts the number of successful executions."
)

failure_counter = meter.create_counter(
    "failure.counter", unit="1", description="Counts the number of failed executions."
)


@tracer.start_as_current_span("lambda_handler")
def lambda_handler(event, context):
    pl = ExtractEvent(event)
    if event['requestContext']['resourcePath'] == '/hello':
        response = spenco_working_func(pl)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "isBase64Encoded": False,
            "body": json.dumps(response)
        }


class ExtractEvent:
    def __init__(self, event):
        (self.resource_path, self.request_id, self.request_ip) = self._extract(event)

    @staticmethod
    @tracer.start_as_current_span("_extract")
    def _extract(event):
        resource_path = event['requestContext']['resourcePath']
        request_id = event['requestContext']['requestId']
        request_ip = event['requestContext']['identity']['sourceIp']
        return resource_path, request_id, request_ip


@tracer.start_as_current_span("spenco_working_func")
def spenco_working_func(pl):
    current_span = trace.get_current_span()
    payload_info = {'resource_path': pl.resource_path, 'request_id': pl.request_id, 'request_ip': pl.request_ip}
    current_span.set_attributes(payload_info)
    return payload_info
