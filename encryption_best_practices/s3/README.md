# 🪣 S3 Encryption Best Practices

This module demonstrates how to enforce encryption and secure access to an Amazon S3 bucket in alignment with the [Encryption best practices for Amazon S3](https://docs.aws.amazon.com/prescriptive-guidance/latest/encryption-best-practices/s3.html) guide.

It includes the following implementations:
- KMS-based encryption at rest
- TLS enforcement (encryption in transit)
- Public access blocking
- S3 policy enforcement
- CloudFront integration
- Optional cross-account access and custom domain configuration

## Features Demonstrated

- **KMS Encryption**
  All S3 objects are encrypted using a customer-managed KMS key with key rotation enabled.

- **Policy Enforcement**
  Denies any upload that:
  - Does not use KMS encryption
  - Grants public access via ACL or grant headers
  - Is made over an insecure (non-SSL) connection

- **CloudFront Integration**
  - CloudFront OAC protects access to S3
  - Bucket is only accessible through the CloudFront distribution

- **AWS Config Rules**
  - `s3-bucket-server-side-encryption-enabled`
  - `s3-bucket-ssl-requests-only`

- **Optional**: Cross-account access and custom domain configuration (commented out but included for demonstration)

---

## Architecture Diagram

TODO: Add diagram here.

> ⚠️ **Important Notes:**
>
> **AWS Config Required**
> This stack uses AWS Config managed rules, which require a configuration recorder and delivery channel to be active in the target region.
> If AWS Config is not yet set up, follow this guide:
> https://docs.aws.amazon.com/config/latest/developerguide/setting-up.html
>
> **ACM Certificate**
> The CloudFront distribution can be configured to use a custom domain with an ACM certificate (commented out in code).
> Certificates must be created in `us-east-1` for CloudFront to use them.
>
> **External Account Access**
> Example permissions to support cross-account access are included but commented out.
> Update the code with a valid account ID to enable.


## Deployment Instructions

Ensure you have Python and AWS CDK installed.

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Bootstrap your AWS environment (only required once per environment/account):
```bash
cdk bootstrap
```

3. Deploy the stack with the specific context and stack name:
```bash
cdk deploy --context topic=encryption-best-practices encbp-01-s3
```

## How to Test

Create a `text.txt` file with any content inside.

1. **Try uploading without SSE-KMS:**

```bash
aws s3 cp test.txt s3://encbp-s3-<aws_account_id>
```
✅ Should fail with Access Denied.

2. **Upload using KMS encryption:**

```bash
aws s3 cp test.txt s3://encbp-s3-<aws_account_id> --sse aws:kms
```
✅ Should succeed.

3. **Attempt upload with public-read ACL:**

```bash
aws s3 cp test.txt s3://encbp-s3-<aws_account_id> --acl public-read --sse aws:kms
```
✅ Should fail.

4. **Try direct S3 access over HTTP — requests will be denied due to `aws:SecureTransport = false`.**

5. **Test CloudFront access (after DNS propagation if custom domain is enabled).**

## Cleanup

To remove all deployed resources for this stack:

```bash
cdk destroy --context topic=encryption-best-practices encbp-01-s3
```
