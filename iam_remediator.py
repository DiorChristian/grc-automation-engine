import json

# 1. READ IAM VIOLATIONS REPORT (CONTAINMENT STAGE)
try:
    with open("iam_violations.json", "r") as f:
        violations = json.load(f)
except FileNotFoundError:
    print("[ERROR] No violations report found. Run iam_auditor.py first!")
    exit()

flagged_users = [item["username"] for item in violations]
print(f"[IAM REMEDIATION STARTED] Found {len(flagged_users)} over-privileged user(s).\n")

# 2. LOAD LIVE IAM POLICY CONFIG
with open("iam_policy.json", "r") as f:
    policies = json.load(f)

remediated_count = 0

# 3. DOWNGRADE WILDCARDS TO LEAST PRIVILEGE (REMEDIATE STAGE)
for policy in policies:
    if policy["username"] in flagged_users:
        print(f"[REMEDIATING] Revoking wildcard admin permissions for '{policy['username']}'...")
        
        # Enforce Least Privilege: Replace wildcard '*' with scoped read-only access
        policy["policy_name"] = "ScopedContractorAccess"
        policy["action"] = "s3:GetObject"
        policy["resource"] = "arn:aws:s3:::contractor-temp-vault/*"
        
        remediated_count += 1

# 4. SAVE COMPLIANT POLICY CONFIG BACK TO DISK (VERIFY & DOCUMENT)
with open("iam_policy.json", "w") as f:
    json.dump(policies, f, indent=2)

print(f"\n[COMPLETE] Successfully downgraded permissions for {remediated_count} user(s).")
print("[VERIFY] Re-run python3 iam_auditor.py to confirm zero policy violations.")