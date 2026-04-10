# AWS Systems Manager Distributor Package and Association CloudFormation Template Guide

## Introduction

This CloudFormation template is designed to create Systems Manager Distributor Packages and State Manager Associations within multiple AWS member accounts, in multiple regions. It facilitates the automated deployment and management of packages via AWS Systems Manager, ensuring consistent and efficient package distribution across your managed instances. The template includes resources for S3 buckets, IAM roles, Lambda functions, and SSM associations, all necessary for the proper functioning of the Systems Manager Distributor.

## Prerequisites

Before deploying this template, ensure you have the following:

- An AWS account with sufficient permissions to create the resources specified in the template.
- Familiarity with AWS CloudFormation, IAM, S3, Lambda, and Systems Manager concepts.
- The AWS CLI installed and configured, if you prefer deploying the template via CLI.

The following are specific prerequisites for successful deployment:

- Complete these steps to register a member account as a stackset delegated administrator account.  AWS member accounts with delegated administrator permissions can create and manage stack sets with service-managed permissions for the organization. [Register a delegated administrator](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-delegated-admin.html)
- In your delegated AWS account, follow these instructions to create a package for your 3rd party software and upload it to Amazon S3. [Create a package](https://docs.aws.amazon.com/systems-manager/latest/userguide/distributor-working-with-packages-create.html#distributor-working-with-packages-create-adv)

## Template Resources

The template will create the following resources:

### S3 Buckets
- `OutputS3Bucket`: Stores the output logs of the AWS Systems Manager Run Command. It is encrypted and has versioning enabled. Public access is blocked for enhanced security.

### IAM Roles
- `CreateSSMDistributorLambdaRole`: Allows the Lambda function to create, update, and delete Systems Manager Distributor Packages and to interact with S3.

### Lambda Functions
- `CreateSSMDistributorLambda`: A Lambda function that handles the creation, updating, and deletion of Systems Manager Distributor Packages.

### Custom Resources
- `CreateSSMDistributorPackage1`: A custom resource that creates the first Systems Manager Distributor Package using the specified parameters.

### SSM Associations
- `Association1`: An SSM Association that schedules the installation or uninstallation of the package on target instances based on specified tags.

## Deploying the Template

### AWS Management Console:

1. Go to the CloudFormation section in the AWS Management Console.
2. Click Create stack > With new resources (standard).
3. Choose Upload a template file, select your file, and click Next.
4. Fill in the required parameters and follow the on-screen instructions to create the stack.

### AWS CLI:

- Save the template to a file, e.g., ssm-distributor-template.yaml.
- Run the following command, replacing `myorg-cpe-centralized-software-distributor-123456789012-us-west-2` and parameter values with your own:

```
aws cloudformation create-stack \
    --stack-name myorg-cpe-centralized-software-distributor-123456789012-us-west-2 \
    --template-body file://centralized-software-distributor-template.yaml \
    --parameters ParameterKey=PackageName1,ParameterValue=XDR \
                 ParameterKey=S3PackageBucketFolder1,ParameterValue=xdr \
                 ParameterKey=Version1,ParameterValue=1.0.0 \
                 ParameterKey=AssociationName1,ParameterValue=CSD-PackageDistributor-XDR \
                 ParameterKey=Action1,ParameterValue=Install \
                 ParameterKey=InstallationType1,ParameterValue=Uninstall and reinstall \
                 ParameterKey=OutputS3KeyPrefix1,ParameterValue=xdr \
                 ParameterKey=ScheduleExpression1,ParameterValue='cron(0 6 ? * SUN *)' \
                 ParameterKey=TargetResourceTagKey1,ParameterValue=AutoDeploy \
                 ParameterKey=TargetResourceTagValue1,ParameterValue=xdr
```

## Conclusion

This CloudFormation template offers a streamlined approach to deploying and managing Systems Manager Distributor Packages and Associations within multiple AWS member accounts, in multiple regions. Customize the template as needed to fit specific package requirements and scheduling preferences.

## Notes

For more information on AWS Systems Manager Distributor and State Manager, refer to the official AWS Systems Manager documentation.