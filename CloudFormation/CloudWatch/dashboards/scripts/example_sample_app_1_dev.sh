#!/bin/bash

services=(
    "ApiGateway"
    "ApplicationELB"
    "CertificateManager"
    "Config"
    "DynamoDB"
    "Events"
    "Firehos"
    "AWS/HealthLake"
    "Lambda"
    "Logs"
    "S3"
    "SNS"
    "AWS/SecretsManager"
    "State"
    "Usage"
)

for service in "${services[@]}"; do
    case $service in
        "ApiGateway")
            aws apigateway get-rest-apis --query "items[].name" --output text
            ;;
        "ApplicationELB")
            aws elbv2 describe-load-balancers --query "LoadBalancers[].LoadBalancerName" --output text
            ;;
        "CertificateManager")
            aws acm list-certificates --query "CertificateSummaryList[].CertificateArn" --output text
            ;;
        "Config")
            aws configservice list-discovered-resources --resource-type="AWS::AllSupported" --query "resourceIdentifiers[].resourceType" --output text
            ;;
        "DynamoDB")
            aws dynamodb list-tables --query "TableNames" --output text
            ;;
        "Events")
            aws events list-rules --query "Rules[].Name" --output text
            ;;
        "Firehos")
            aws firehose list-delivery-streams --query "DeliveryStreamNames" --output text
            ;;
        "AWS/HealthLake")
            aws healthlake describe-fhir-exports --query "FhirExportJobPropertiesList[].DatastoreName" --output text
            ;;
        "Lambda")
            aws lambda list-functions --query "Functions[].FunctionName" --output text
            ;;
        "Logs")
            aws logs describe-log-groups --query "logGroups[].logGroupName" --output text
            ;;
        "S3")
            aws s3api list-buckets --query "Buckets[].Name" --output text
            ;;
        "SNS")
            aws sns list-topics --query "Topics[].TopicArn" --output text
            ;;
        "AWS/SecretsManager")
            aws secretsmanager list-secrets --query "SecretList[].Name" --output text
            ;;
        "State")
            aws stepfunctions list-state-machines --query "stateMachines[].stateMachineArn" --output text
            ;;
        "Usage")
            aws ce get-dimension-values --time-period Start=2023-01-01,End=2023-12-31 --dimension "USAGE_TYPE" --query "DimensionValues[].Value" --output text
            ;;
        *)
            echo "Unknown service: $service"
            ;;
    esac
done
