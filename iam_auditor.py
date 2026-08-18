import json
import sys

print("[IAM AUDITOR STARTED] Evaluating Access Policies for Wildcard Exposure...\n")

POLICY_FILE = "iam_policy.json"

try:
    with open(POLICY_FILE, "r") as f:
        policies = json.load(f)
except Exception as e:
    print(f"[CRITICAL ERROR] Failed to load IAM policies: {str(e)}")
    sys.exit(2)

violations = []

for policy in policies:
    policy_name = policy.get("PolicyName", "UNKNOWN_POLICY")
    role = policy.get("Role", "UNKNOWN_ROLE")
    statements = policy.get("Statements") or []

    for stmt in statements:
        effect = stmt.get("Effect", "")
        action = stmt.get("Action", "")
        resource = stmt.get("Resource", "")

        actions = action if isinstance(action, list) else [action]

        is_full_admin = effect == "Allow" and "*" in actions and resource == "*"
        is_wildcard_service = effect == "Allow" and any("*" in a for a in actions) and resource == "*"

        if is_full_admin or is_wildcard_service:
            violations.append({
                "PolicyName": policy_name,
                "Role": role,
                "Action": action,
                "Resource": resource,
                "Risk": "CRITICAL_OVER_PRIVILEGED"
            })
            print(f"[VIOLATION DETECTED] Policy '{policy_name}' ({role}) grants wildcards -> Action: {action} | Resource: {resource}")

with open("iam_violations.json", "w") as out:
    json.dump(violations, out, indent=2)

print("\n--------------------------------------------------")
if len(violations) > 0:
    print(f"[COMPLETED] Found {len(violations)} over-privileged IAM policy violation(s). Exiting with status 1.")
    sys.exit(1)
else:
    print("[COMPLETED] All IAM policies compliant with Least Privilege. Exiting with status 0.")
    sys.exit(0)