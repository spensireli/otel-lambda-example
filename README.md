# OTEL with AWS Lambda and AWSEMF Exporter

This repository showcases how to use OpenTelemetry with AWS Lambda and X-Ray for enhanced observability.

For information on what each component is doing see the [Project Breakdown](#Project Breakdown) section.

## Deploying This Project

This project requires AWS CDK `2.85.0` or higher. 

```bash scripts/build.sh```

```cdk deploy```

## Deployed Endpoints

### /hello
This endpoint operates normally and will respond with a 200 along with trace information.

### /sleepy
This endpoint simulates long running processes and takes 10 seconds to complete. You can 
see in the trace the time it has taken to run the particular function.

### /broken
This endpoint intentionally does not work. The call will fail and you can see the trace and exactly which 
function failed using OTEL + X-Ray. 

## What is OpenTelemetry?

[OpenTelemetry](https://opentelemetry.io/) is a collection of tools, APIs, and SDKs. Use it to instrument, generate, collect, and export telemetry data (metrics, logs, and traces) to help you analyze your software’s performance and behavior.

Some benefits to using OTEL over proprietary distributing tracing technology are:

- Standardization of how telemetry data is collected and reported on.
- Prevents vendor lock-in. 
- Provides out of the box support with a number of third-party [vendors](https://opentelemetry.io/ecosystem/vendors/).
- OpenSource & Free

# Project Breakdown

## Lessons Learned

- Documentation explaining the integration of OTEl and X-Ray is lacking. Lots of articles but little explains the how and why.
- OTEL Version changes can impact operatbility with X-Ray.
- How OTEL is used in a production setting.
- How to send OTEL Metrics to CloudWatch Metrics using AWS EMF Exporter.
- There exists an OTEL Lambda Layer maintained by AWS

## OTEL Layer

[Here](./infrastructure/spenco.py#L91) we see a Lambda Layer that is being imported that contains the necessary OTEL packages.
After doing some digging I was able to find the information located on an [AWS OTEL Project](https://aws-otel.github.io/docs/getting-started/lambda/lambda-python) page.
This Layer is owned and managed by AWS for use with OTEL. 

The consistency of this layer seems to be spotty. So it may be worth rolling your own ADOT layer and sharing it with your accounts. 

## Tracer and Decorator Usage

In the lambda function itself we must first initialize a [tracer](./lib/lambda_code/spenco/spenco.py#L7).
We will use this tracer throughout the entire function. 

In each function within our Lambda Function, you can see calling of the [decorator](./lib/lambda_code/spenco/spenco.py#L18).
The value I am passing to the decorator is arbitrary and will show up in the Trace. I decided that it made
most sense to use the name of the function. 

## Attributes

In other parts of the lambda code you can see that I am setting particular [attributes](./lib/lambda_code/spenco/spenco.py#L72) I want to return to OTEL. 
These attributes in the case of this example will actually be published to AWS X-Ray and visible within the AWS Console. 
This can be useful for adding metadata about the execution to your traces. 

## Metrics

Metrics can be published but first they must be [initialized](./lib/lambda_code/spenco/spenco.py#L8-15). 

Here I am creating a simple success and failure metric. The metric is then called when a [successful operation](./lib/lambda_code/spenco/spenco.py#L85) happens, or when a [failure](./lib/lambda_code/spenco/spenco.py#L97)
happens. 

By Publishing metrics alone they do not end up in AWS CloudWatch. For this we must use the AWS EMF Exporter.

## AWS EMF Exporter

In the [config.yaml](./lib/config.yaml#L10-L19) you can see an example configuration of the AWS EMF Exporter that OTEL will use. 
This is required if you wish to publish metrics to AWS CloudWatch. CloudWatch Metrics format are different from OTEL Metrics. 
Thus they must be converted into an AWS EMF Format. That is exactly what the exporter does. 

## Exception Recording

When a failure does occur it is often useful to have the exception that was raised without having to comb through logs.
Using OTEL you can [record exceptions](./lib/lambda_code/spenco/spenco.py#L98). The contents of the exception will be visible in 
X-Ray with the trace.