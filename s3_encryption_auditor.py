import sys

def audit_s3_encryption(payload):
    """
    NIST SP 800-53 SC-28: Protection of Information at Rest
    Validates that S3 Server-Side Encryption (SSE) is enabled.
    """
    bucket_name = payload.get("BucketName", "Unknown-Bucket")
    sse_config = payload.get("ServerSideEncryptionConfiguration")

    print(f"\n[AUDIT] Running SC-28 Encryption Check for S3 Bucket: {bucket_name}")

    if not sse_config:
        print(f"[FAIL] NIST SC-28 Violation: S3 Bucket '{bucket_name}' has NO encryption configured!")
        print("[CIRCUIT BREAKER] Tripping pipeline circuit breaker (exit code 1)...")
        sys.exit(1)

    print(f"[PASS] NIST SC-28 Compliant: S3 Bucket '{bucket_name}' is properly encrypted.")
    return True
if __name__ == "__main__":
    payload_fail = {
        "BucketName": "prod-user-analytics-data",
        "Region": "us-west-2",
        "ServerSideEncryptionConfiguration": None,
        "PublicAccessBlock": True
    }
    audit_s3_encryption(payload_fail)