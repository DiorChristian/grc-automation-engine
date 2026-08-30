# Service Control Policy to enforce NIST compliance guardrails
resource "aws_organizations_policy" "nist_guardrails_scp" {
  name        = "NISTCloudSentinelGuardrails"
  description = "Prevents disabling core security services and tampering with audit logs."
  type        = "SERVICE_CONTROL_POLICY"

  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "DenyCloudTrailTampering"
        Effect   = "Deny"
        Action   = [
          "cloudtrail:DeleteTrail",
          "cloudtrail:StopLogging",
          "cloudtrail:UpdateTrail",
          "cloudtrail:PutEventSelectors"
        ]
        Resource = "*"
      },
      {
        Sid      = "DenyAuditBucketDestruction"
        Effect   = "Deny"
        Action   = [
          "s3:DeleteBucket",
          "s3:DeleteBucketPolicy",
          "s3:PutBucketPublicAccessBlock"
        ]
        Resource = [
          "arn:aws:s3:::nist-sentinel-immutable-audit-vault",
          "arn:aws:s3:::nist-sentinel-immutable-audit-vault/*"
        ]
      }
    ]
  })
}