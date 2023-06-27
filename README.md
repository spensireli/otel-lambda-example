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

[Here](./infrastructure/spenco.py#L91)
