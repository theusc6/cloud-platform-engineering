# AWS-Nuke CloudFormation Template Guide

## Introduction

AWS-Nuke is a tool designed to help you remove resources within an AWS account. The tool is highly useful for cleaning up test environments or ensuring that no unnecessary resources are left running in your AWS account, which could lead to unwanted costs. This CloudFormation template simplifies the deployment of AWS-Nuke by setting up the necessary AWS resources, including S3 buckets for configuration, IAM roles for permissions, and an ECS cluster to run AWS-Nuke tasks. It is currently scheduled to run each Monday @ 6AM PST.

**WARNING** This is an extremely destructive tool. Run **only** in non-production, sandbox accounts. Usage of this template will result in the deletion of all resoruces in an AWS account.

## Prerequisites

Before deploying this template, ensure you have the following:

- A non-production AWS account with sufficient permissions to create the resources specified in the template.
- Familiarity with AWS CloudFormation, IAM, S3, ECS, and VPC concepts.
- The AWS CLI installed and configured, if you prefer deploying the template via CLI.

## Template Resources 

The template will create the following resources:

### S3 Buckets
- s3NukeConfigBucket: Stores the AWS-Nuke configuration file. It is encrypted and has versioning enabled to keep track of changes. Public access is blocked for enhanced security.

### IAM Roles
- iamEcsExecutionRole: Allows ECS tasks to call AWS services on your behalf.
- iamEcsTaskRole: Grants the AWS-Nuke task the permissions it needs to list and delete resources across your AWS account.
- iamEventsRole: Used by CloudWatch Events to trigger the ECS task based on the specified schedule.

### Security Groups
- nuke-sg: Security group for the ECS task, ensuring it can access the necessary AWS resources securely.

### Log Groups
- logsNukeGroup: Captures logs from the execution of AWS-Nuke, useful for auditing and troubleshooting.

### ECS Cluster & Task Definition
- ecsCluster: The ECS cluster where the AWS-Nuke tasks will run.
- ecsTaskDefinition: Defines the AWS-Nuke task, including the Docker image to use, the required CPU and memory, and the command to execute AWS-Nuke.

### EventBridge Rule
- nuke-task-scheduler: Schedules the AWS-Nuke task to run at specified times using a cron expression.

## Deploying the Template

### AWS Management Console:

1) Go to the CloudFormation section in the AWS Management Console.
2) Click Create stack > With new resources (standard).
3) Choose Upload a template file, select your file, and click Next.
4) Fill in the required parameters, such as pVpcId and pSubnetIds, and follow the on-screen instructions to create the stack.

The network configurations are critically important to ensuring that the aws-nuke task can run. This will require the following:

- A subnet in which the ECS task can reach the internet

This can be accomplished via a variety of ways, but the recommendation is:

- (2) Subnets - (1) private subnet & (1) public subnet
- (2) Route Tables - (1) private route table & (1) public route table
- (1) Internet Gateway
- (1) NAT Gateway
- (1) Security Group (Created as from the CloudFormation template - "nuke-sg")

The NAT Gateway will be placed into the public subnet. 

The public route table will direct all 0.0.0.0/0 traffic from the public subnet to the internet gateway. The private route table will direct 0.0.0.0/0 traffic from the private subnet to the NAT gateway. 

In essence:
Here’s how traffic typically flows from a private subnet through a NAT Gateway to the Internet Gateway, and out to the internet:

An instance in a private subnet sends a request to an external service on the internet.
- The request is routed to the NAT Gateway based on the VPC's route table associated with the private subnet.
- The NAT Gateway translates the source private IP address of the instance to the NAT Gateway’s IP address and forwards the request to the IGW.
- The IGW then sends the request out to the internet.
- The response follows the reverse path: from the internet to the IGW, to the NAT Gateway, and finally back to the instance in the private subnet.

### AWS CLI:

- Save the template to a file, e.g., aws-nuke-template.yaml.
- Run the following command, replacing ```<your-stack-name>```, ```<VpcId>```, and ```<SubnetIds>``` with your values:
  
```aws cloudformation create-stack```

```--stack-name <your-stack-name> ```

```--template-body file://aws-nuke-template.yaml```

```--parameters ParameterKey=pVpcId,ParameterValue=<VpcId> ParameterKey=pSubnetIds,ParameterValue=<SubnetId1>\\,<SubnetId2>```

## Conclusion

This CloudFormation template offers a streamlined approach to deploying AWS-Nuke within a given non-production account, enabling regular cleanup tasks to ensure cost-efficiency and resource optimization. Customize the template as needed to fit specific resource or account requirements as well as scheduling preferences.

## Notes

References to original AWS-Nuke documentation can be found here: https://github.com/rebuy-de/aws-nuke/tree/main
