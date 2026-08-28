import json
import sys

print("[S3 AUDITOR STARTED] Scanning storage configurations with chaos handling...\n")

INVENTORY_FILE = "corrupted_s3.json"

try:
    with open(INVENTORY_FILE, "r") as f:
        buckets = json.load(f)
except FileNotFoundError:
    print(f"[CRITICAL ERROR] Storage inventory '{INVENTORY_FILE}' not found.")
    sys.exit(2)
except json.JSONDecodeError:
    print(f"[CRITICAL ERROR] Storage inventory '{INVENTORY_FILE}' has invalid JSON syntax.")
    sys.exit(2)

violations = []
execution_error = False

for bucket in buckets:
    try:
        bucket_name = bucket.get("bucket_name", "UNKNOWN_BUCKET")
        
        # Defensive check for public access block configuration
        pab = bucket.get("public_access_block") or {}
        block_public_acls = pab.get("BlockPublicAcls", False)
        block_public_policy = pab.get("BlockPublicPolicy", False)
        
        # Defensive check for server-side encryption
        encryption = bucket.get("encryption")

        # Evaluate S3 compliance rules
        is_public = not (block_public_acls and block_public_policy)
        is_unencrypted = encryption is None or encryption == "NONE"

        if is_public or is_unencrypted:
            finding = {
                "bucket_name": bucket_name,
                "is_public": is_public,
                "unencrypted": is_unencrypted,
                "risk_level": "CRITICAL" if (is_public and is_unencrypted) else "HIGH"
            }
            violations.append(finding)
            print(f"[VIOLATION DETECTED] Bucket '{bucket_name}' -> Public: {is_public} | Unencrypted: {is_unencrypted}")

    except Exception as e:
        print(f"[NON-FATAL ERROR] Failed to process bucket entry '{bucket_name}': {str(e)}")
        execution_error = True

# Write out violation evidence
with open("s3_violations.json", "w") as out:
    json.dump(violations, out, indent=2)

if execution_error:
    print("\n[COMPLETED WITH ERRORS] S3 audit completed with non-fatal items.")
    sys.exit(2)
elif len(violations) > 0:
    print(f"\n[COMPLETED] Found {len(violations)} non-compliant bucket(s). Exiting with status 1.")
    sys.exit(1)
else:
    print("\n[COMPLETED] All storage buckets compliant. Exiting with status 0.")
    sys.exit(0)