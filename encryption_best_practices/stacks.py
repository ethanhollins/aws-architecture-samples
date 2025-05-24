from constructs import Construct
from decorators import topic
from encryption_best_practices.s3.stack import S3EncryptionBestPracticesStack


"""
Stacks for: Encryption Best Practices

This file defines the deployable infrastructure stacks related to encryption best practices,
such as enforcing S3 encryption, KMS key usage, and more.

The infrastructure patterns in this module are based on the official AWS Prescriptive Guidance:
https://docs.aws.amazon.com/prescriptive-guidance/latest/encryption-best-practices

How to deploy:

Deploy all stacks for this topic:
    cdk deploy --context topic=encryption-best-practices

Deploy selected stacks for this topic:
    cdk deploy --context topic=encryption-best-practices <stack_names>

Stack naming convention:
Each stack is prefixed for clarity and sorting. For example:
    - encbp-01-s3         → S3 Encryption Best Practices
    - encbp-02-kms        → KMS Encryption Best Practices
"""


@topic("encryption-best-practices")
def register_stacks(app: Construct):
    S3EncryptionBestPracticesStack(app, "encbp-01-s3")
    # KMSEncryptionBestPracticesStack(app, "encbp-02-kms")
