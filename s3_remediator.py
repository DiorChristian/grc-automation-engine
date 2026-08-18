import json

# 1. READ INCIDENT REPORT (CONTAINMENT)
try:
    with open("s3_incident_report.json", "r") as report_file:
        incidents = json.load(report_file)
except FileNotFoundError:
    print("[ERROR] No incident report found. Run s3_auditor.py first!")
    exit()

flagged_buckets = [item["bucket_name"] for item in incidents]
print(f"[REMEDIATION STARTED] Found {len(flagged_buckets)} buckets requiring remediation.\n")

# 2. READ LIVE CLOUD CONFIG
with open("aws_s3_data.json", "r") as config_file:
    buckets = json.load(config_file)

remediated_count = 0

# 3. APPLY AUTO-REMEDIATION (REMEDIATE)
for bucket in buckets:
    if bucket["bucket_name"] in flagged_buckets:
        print(f"[FIXING] Remediating security controls for {bucket['bucket_name']}...")
        
        # Security Rule 1: Set IsPublic to False
        bucket["policy_status"]["IsPublic"] = False
        
        # Security Rule 2: Enable Public Access Block
        bucket["public_access_block"]["BlockPublicAcls"] = True
        
        # Security Rule 3: Revoke Wildcard ACLs
        bucket["acl_grants"] = ["OwnerOnly"]
        
        remediated_count += 1

# 4. SAVE COMPLIANT CONFIG BACK TO DISK (VERIFY & DOCUMENT)
with open("aws_s3_data.json", "w") as config_file:
    json.dump(buckets, config_file, indent=2)

print(f"\n[COMPLETE] Successfully remediated {remediated_count} buckets.")
print("[VERIFY] Re-run python3 s3_auditor.py to verify full compliance.")