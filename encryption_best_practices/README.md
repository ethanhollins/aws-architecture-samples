# Encryption Best Practices

This folder implements hands-on sample code based on the [Encryption best practices and features for AWS services](https://docs.aws.amazon.com/prescriptive-guidance/latest/encryption-best-practices/welcome.html) guide. The goal is to help you understand and apply encryption techniques aligned with the [AWS Well-Architected Framework (WAFR)](https://aws.amazon.com/architecture/well-architected/).

Each subfolder contains a self-contained CDK stack demonstrating the best practice standards to implement encryption for each AWS service.

## Folder Structure

| Folder        | Description |
|---------------|----------------------------------------------------------------------------|
| `s3/`         | [Handling S3 bucket policy encryption enforcement and HTTPS-only access](./s3) |
| `kms/`        | *(Planned)* KMS encryption best practices |
| `rds/`        | *(Planned)* RDS encryption best practices |
| `cloudtrail/` | *(Planned)* CloudTrail encryption best practices |
| `dynamodb/`   | *(Planned)* DynamoDB encryption best practices |
| `ec2/`        | *(Planned)* EC2 and EBS encryption best practices |
| `ecr/`        | *(Planned)* ECR encryption best practices |
| `ecs/`        | *(Planned)* ECS encryption best practices |
| `sdk/`        | *(Planned)* AWS Encryption SDK encryption best practices |
| `lambda/`     | *(Planned)* Lambda best encryption practices |
| `secrets/`    | *(Planned)* Secrets Manager encryption best practices |
| `vpc/`        | *(Planned)* VPC encryption best practices |

All stacks are independently deployable and are also registered in this folder’s `stacks.register_stacks`.

## Deployment Instructions

> ⚠️ **Important Note:**
> Some stacks rely on AWS Config managed rules (e.g., to monitor encryption or enforce compliance).
> These require a **Configuration Recorder** and **Delivery Channel** to be set up in the AWS region where you're deploying.
> If AWS Config is not already set up in your account, follow the [AWS Config setup guide](https://docs.aws.amazon.com/config/latest/developerguide/setting-up.html) before deploying.

Ensure you have Python and AWS CDK installed.

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Bootstrap your AWS environment (only required once per environment/account):
```bash
cdk bootstrap
```

3. Deploy the stack with the specific context and optionally the stack name:
```bash
cdk deploy --context topic=encryption-best-practices <stack_name>
```

## Cleanup

To remove all deployed resources for the encryption best practices topic:

```bash
cdk destroy --context topic=encryption-best-practices
```

Optionally you can provide the stack name to destroy a specific stack:

```bash
cdk destroy --context topic=encryption-best-practices <stack_name>
```
