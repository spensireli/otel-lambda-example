import json
import time
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
    if event['requestContext']['resourcePath'] == '/sleepy':
        response = spenco_sleepy_func(pl)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "isBase64Encoded": False,
            "body": json.dumps(response)
        }
    if event['requestContext']['resourcePath'] == '/broken':
        response = broken_function(pl)
        return {
            "statusCode": 502,
            "headers": {
                "Content-Type": "application/json"
            },
            "isBase64Encoded": False,
            "body": json.dumps(response)
        }

class ExtractEvent:
    def __init__(self, event):
        (self.resource_path, self.request_id, self.request_ip, self.trace_id) = self._extract(event)

    @staticmethod
    @tracer.start_as_current_span("_extract")
    def _extract(event):
        resource_path = event['requestContext']['resourcePath']
        request_id = event['requestContext']['requestId']
        request_ip = event['requestContext']['identity']['sourceIp']
        trace_id = event['headers']['X-Amzn-Trace-Id'].split('=')[1]
        return resource_path, request_id, request_ip, trace_id


@tracer.start_as_current_span("spenco_working_func")
def spenco_working_func(pl):
    current_span = trace.get_current_span()
    trace_url = f'https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#xray:traces/{pl.trace_id}'
    payload_info = {'resource_path': pl.resource_path, 'request_id': pl.request_id, 'request_ip': pl.request_ip,
                    'trace_id': pl.trace_id, 'trace_url': trace_url}
    current_span.set_attributes(payload_info)
    success_counter.add(1)
    return payload_info


@tracer.start_as_current_span("spenco_sleepy_func")
def spenco_sleepy_func(pl):
    current_span = trace.get_current_span()
    time.sleep(10)
    trace_url = f'https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#xray:traces/{pl.trace_id}'
    payload_info = {'resource_path': pl.resource_path, 'request_id': pl.request_id, 'request_ip': pl.request_ip,
                    'trace_id': pl.trace_id, 'trace_url': trace_url}
    current_span.set_attributes(payload_info)
    success_counter.add(1)
    return payload_info

@tracer.start_as_current_span("broken_function")
def broken_function(pl):
    current_span = trace.get_current_span()
    try:
        trace_url = f'https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#xray:traces/{pl.trace_id}'
        payload_info = {'resource_path': pl.resource_path, 'request_id': pl.request_id, 'request_ip': pl.request_ip,
                        'trace_id': pl.trace_id, 'trace_url': trace_ur}
        current_span.set_attributes(payload_info)
    except Exception as e:
        failure_counter.add(1)
        current_span.record_exception(e)
        raise e
