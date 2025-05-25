from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_kms as kms,
    aws_iam as iam,
    aws_config as config,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class S3EncryptionBestPracticesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """
        KMS Resources
        """

        kms_key = kms.Key(
            self,
            "EncbpKey",
            alias="alias/encbp/s3-key",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        """
        S3 Bucket Resources
        """

        # S3 Bucket
        encbp_s3_bucket = s3.Bucket(
            self,
            "EncbpS3Bucket",
            bucket_name=f"encbp-s3-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=kms_key,
        )

        # Enforce SSE-S3 encryption on S3 put object action
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyObjectsThatAreNotSSEKMS",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:PutObject"],
                resources=[f"{encbp_s3_bucket.bucket_arn}/*"],
                conditions={
                    "StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}
                },
            )
        )

        # Deny S3 object public read ACLs
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyPublicReadACL",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:PutObject", "s3:PutObjectAcl"],
                resources=[f"{encbp_s3_bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {
                        "s3:x-amz-acl": [
                            "public-read",
                            "public-read-write",
                            "authenticated-read",
                        ]
                    }
                },
            )
        )

        # Deny S3 object public read grants
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyPublicReadGrant",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:PutObject", "s3:PutObjectAcl"],
                resources=[f"{encbp_s3_bucket.bucket_arn}/*"],
                conditions={
                    "StringLike": {
                        "s3:x-amz-grant-read": [
                            "*http://acs.amazonaws.com/groups/global/AllUsers*",
                            "*http://acs.amazonaws.com/groups/global/AuthenticatedUsers*",
                        ]
                    }
                },
            )
        )

        # Deny S3 bucket public read ACLs
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyPublicListACL",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:PutBucketAcl"],
                resources=[encbp_s3_bucket.bucket_arn],
                conditions={
                    "StringEquals": {
                        "s3:x-amz-acl": [
                            "public-read",
                            "public-read-write",
                            "authenticated-read",
                        ]
                    }
                },
            )
        )

        # Deny S3 bucket public read grants
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyPublicListGrant",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:PutBucketAcl"],
                resources=[encbp_s3_bucket.bucket_arn],
                conditions={
                    "StringLike": {
                        "s3:x-amz-grant-read": [
                            "*http://acs.amazonaws.com/groups/global/AllUsers*",
                            "*http://acs.amazonaws.com/groups/global/AuthenticatedUsers*",
                        ]
                    }
                },
            )
        )

        # Enforce SSL for all S3 actions
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowSSLRequestsOnly",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:*"],
                resources=[
                    encbp_s3_bucket.bucket_arn,
                    f"{encbp_s3_bucket.bucket_arn}/*",
                ],
                conditions={"Bool": {"aws:SecureTransport": "false"}},
            )
        )

        """
        AWS Config Resources
        """

        # Enforce S3 buckets must have server-side encryption enabled
        config.ManagedRule(
            self,
            "S3BucketSSEEnabledRule",
            identifier=config.ManagedRuleIdentifiers.S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED,
            rule_scope=config.RuleScope.from_resource(
                config.ResourceType.S3_BUCKET, encbp_s3_bucket.bucket_name
            ),
        )

        # S3 requests must enforce SSL
        config.ManagedRule(
            self,
            "S3BucketSSLRequestsOnlyRule",
            identifier=config.ManagedRuleIdentifiers.S3_BUCKET_SSL_REQUESTS_ONLY,
            rule_scope=config.RuleScope.from_resource(
                config.ResourceType.S3_BUCKET, encbp_s3_bucket.bucket_name
            ),
        )

        """
        CloudFront Resources

        These policies restrict access to S3 objects so they can only be served through
        CloudFront. This is recommended for web content because:

        - **Security**: Prevents direct access to S3 URLs, reducing the risk of data exposure.
        - **Access Control**: Enables features like signed URLs and cookies for fine-grained control.
        - **Performance**: Uses global edge caching to reduce latency and offload S3 traffic.
        - **TLS Enforcement**: Ensures HTTPS delivery via CloudFront, not S3’s public endpoints.

        Use this setup when serving static or media content to users over the web.
        Avoid using it for backend or internal-only S3 access unless CloudFront adds clear value.
        """

        # Origin Access Control
        oac = cloudfront.CfnOriginAccessControl(
            self,
            "EncbpOAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name="encbp-oac",
                origin_access_control_origin_type="s3",
                signing_protocol="sigv4",
                signing_behavior="always",
            ),
        )

        # CloudFront Distribution
        distribution = cloudfront.Distribution(
            self,
            "EncbpCDN",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(
                    encbp_s3_bucket, origin_access_control_id=oac.attr_id
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
            ),
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
            enable_logging=False,
        )

        # Allow read access to CloudFront distribution
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowCloudFrontServicePrincipalReadOnly",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                actions=["s3:GetObject"],
                resources=[f"{encbp_s3_bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {"AWS:SourceArn": distribution.distribution_arn}
                },
            )
        )

        # external_account_id = "123456789012"  # Commented out since external account access is not currently in use

        # Deny read access except CloudFront distribution
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyAllReadAccessExceptCloudFront",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:GetObject"],
                resources=[f"{encbp_s3_bucket.bucket_arn}/*"],
                conditions={
                    "StringNotEquals": {"AWS:SourceArn": distribution.distribution_arn},
                    # # External account access commented out for now; remove comments if enabling cross-account access
                    # "StringNotEqualsIfExists": {
                    #     "aws:PrincipalArn": f"arn:aws:iam::{external_account_id}:root"
                    # }
                },
            )
        )

        # Deny all S3 access except CloudFront distribution and AWS Account
        encbp_s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyAllExceptCloudFrontAndAccount",
                effect=iam.Effect.DENY,
                principals=[iam.ArnPrincipal("*")],
                actions=["s3:*"],
                resources=[
                    encbp_s3_bucket.bucket_arn,
                    f"{encbp_s3_bucket.bucket_arn}/*",
                ],
                conditions={
                    "StringNotEqualsIfExists": {
                        "AWS:SourceArn": distribution.distribution_arn,
                        "aws:PrincipalAccount": [
                            self.account,
                            # # External account ID excluded for now. If enabling external access,
                            # # uncomment above and define `external_account_id` appropriately.
                            # external_account_id
                        ],
                    }
                },
            )
        )

        """
        Cross Account S3 Access

        The following section demonstrates how to allow an external AWS account to access
        resources such as a KMS key and an S3 bucket. This is currently commented out
        because the external account ID is not in use.

        To enable:
        1. Uncomment all relevant lines.
        2. Replace the placeholder account ID with the real external AWS account ID.
        3. Ensure necessary trust relationships and roles are properly configured.
        """

        # # Allow external account to use the KMS key for decrypting and generating data keys.
        # kms_key.add_to_resource_policy(
        #     iam.PolicyStatement(
        #         sid="AllowExternalAccountToUseKey",
        #         principals=[iam.AccountPrincipal(external_account_id)],
        #         actions=[
        #             "kms:Decrypt",
        #             "kms:ReEncryptFrom",
        #             "kms:ReEncryptTo",
        #             "kms:GenerateDataKey*",
        #             "kms:DescribeKey",
        #         ],
        #         resources=["*"],  # Must be "*" for KMS operations
        #     )
        # )

        # # Grant external account read-only access to objects in the S3 bucket
        # encbp_s3_bucket.add_to_resource_policy(
        #     iam.PolicyStatement(
        #         sid="AllowExternalAccountReadAccess",
        #         principals=[iam.AccountPrincipal(external_account_id)],
        #         actions=[
        #             "s3:GetObject",
        #             "s3:GetObjectVersion",
        #             "s3:ListBucket",
        #             "s3:GetBucketLocation"
        #         ],
        #         resources=[
        #             encbp_s3_bucket.bucket_arn,
        #             f"{encbp_s3_bucket.bucket_arn}/*"
        #         ],
        #     )
        # )
