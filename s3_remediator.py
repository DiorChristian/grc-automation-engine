import json
import sys
from datetime import datetime

print("[S3 AUTO-REMEDIATOR STARTED] Active lockdown engaged...\n")

INVENTORY_FILE = "corrupted_s3.json"

try:
    with open(INVENTORY_FILE, "r") as f:
        buckets = json.load(f)
except Exception as e:
    print(f"[CRITICAL ERROR] Failed to load bucket inventory: {str(e)}")
    sys.exit(2)

remediation_log = []

for bucket in buckets:
    bucket_name = bucket.get("bucket_name", "UNKNOWN_BUCKET")
    
    pab = bucket.get("public_access_block") or {}
    is_public = not (pab.get("BlockPublicAcls", False) and pab.get("BlockPublicPolicy", False))
    encryption = bucket.get("encryption")
    is_unencrypted = encryption is None or encryption == "NONE"

    actions_taken = []

    # Auto-Remediate Public Access
    if is_public:
        bucket["public_access_block"] = {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
        actions_taken.append("ENFORCED_PUBLIC_ACCESS_BLOCK")
        print(f"[AUTO-FIX] Applied Public Access Block to '{bucket_name}'")

    # Auto-Remediate Encryption
    if is_unencrypted:
        bucket["encryption"] = "AES256"
        actions_taken.append("ENFORCED_SERVER_SIDE_ENCRYPTION_AES256")
        print(f"[AUTO-FIX] Applied AES256 Encryption to '{bucket_name}'")

    if actions_taken:
        remediation_log.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "bucket_name": bucket_name,
            "remediations": actions_taken,
            "status": "REMEDIATED_COMPLIANT"
        })

# Export proof of self-healing for compliance auditing
with open("remediation_audit.json", "w") as out:
    json.dump(remediation_log, out, indent=2)

# Save updated compliant inventory back to the file
with open(INVENTORY_FILE, "w") as f:
    json.dump(buckets, f, indent=2)

print(f"\n[REMEDIATION COMPLETE] Fixed {len(remediation_log)} bucket(s). Evidence exported to remediation_audit.json.")