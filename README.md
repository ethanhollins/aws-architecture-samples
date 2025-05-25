# AWS Architecture Center Code Samples

This repository contains sample code implementations for the [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) and its related AWS Architecture Center guides.

It showcases production-grade patterns and best practices for a wide range of use cases and implementation types — including storage, security, compute, network architecture, compliance, and more.

Each guide has its own folder containing self-contained, deployable stacks and explanatory documentation with architecture diagrams. These are designed to help individuals and teams implement secure, reliable, cost-effective, and operationally robust solutions in the cloud.

## Key Goals

- Reinforce Well-Architected Framework principles
- Provide real-world, hands-on code for AWS best practices
- Support a wide range of application types and deployment patterns

## Guides

- [`encryption_best_practices/`](./encryption_best_practices) — Implements encryption and key management best practices using S3, KMS, and AWS Config.

> More guides coming soon. Stay tuned!

## Getting Started

You’ll need:

- AWS CLI & credentials configured
- Python 3.8+
- AWS CDK installed

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Bootstrap your AWS environment (only required once per environment/account):
```bash
cdk bootstrap
```

3. Deploy the stack with a specific context and optionally the stack name (e.g. topic=encryption-best-practices):
```bash
cdk deploy --context topic=<topic_name> <stack_name>
```

## Cleanup

To remove all deployed resources:

```bash
cdk destroy
```

Optionally you can provide the context for quicker compilation and stack name to destroy a specific stack:

```bash
cdk destroy --context topic=<topic_name> <stack_name>
```

## About the Author

This repository is maintained by [Ethan Hollins](https://www.linkedin.com/in/ethanhollins/), a certified [AWS Solutions Architect – Professional](https://aws.amazon.com/certification/certified-solutions-architect-professional/), with a focus on spreading digestible best practice sample code based on AWS WAFR guides.
