# otel-lambda-example

This repository showcases how to use OpenTelemetry with AWS Lambda and X-Ray for enhanced observability.

## Deploying This Project

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

## What is X-Ray?

[AWS X-Ray](https://aws.amazon.com/xray/) provides a complete view of requests as they travel through your application and filters visual data across payloads, functions, traces, services, APIs, and more with no-code and low-code motions.

## OTEL Components Explained





