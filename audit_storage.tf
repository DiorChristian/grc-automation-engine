# Central WORM-Compliant Audit Storage Bucket for Forensic Snapshots & Logs
resource "aws_s3_bucket" "compliance_audit_logs" {
  bucket        = "nist-sentinel-immutable-audit-vault"
  force_destroy = false
}

# Enforce Versioning (Required for Object Lock)
resource "aws_s3_bucket_versioning" "audit_versioning" {
  bucket = aws_s3_bucket.compliance_audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable Object Lock in Compliance Mode (Write-Once-Read-Many / WORM)
resource "aws_s3_bucket_object_lock_configuration" "worm_lock" {
  bucket = aws_s3_bucket.compliance_audit_logs.id

  rule {
    default_retention {
      mode  = "COMPLIANCE"
      years = 7 # Retain audit logs and pre-remediation forensic snapshots for 7 years to meet strict regulatory standards (SOC 2, PCI, HIPAA)
    }
  }

  depends_on = [aws_s3_bucket_versioning.audit_versioning]
}

# Enforce AES256 Server-Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "audit_encryption" {
  bucket = aws_s3_bucket.compliance_audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access to the audit bucket completely
resource "aws_s3_bucket_public_access_block" "audit_public_block" {
  bucket                  = aws_s3_bucket.compliance_audit_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}