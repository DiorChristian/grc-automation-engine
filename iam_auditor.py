import json

# Load raw IAM security policy
with open("iam_policy.json", "r") as f:
    policies = json.load(f)

print("[IAM AUDIT STARTED] Evaluating policies for Least Privilege violations...\n")

flagged_users = []

for policy in policies:
    user = policy["username"]
    action = policy["action"]
    resource = policy["resource"]

    # Check for dangerous wildcard admin permissions
    if action == "*" and resource == "*":
        print(f"[CRITICAL VIOLATION] User '{user}' has FULL ADMIN ACCESS ('*':'*')!")
        flagged_users.append({
            "username": user,
            "policy": policy["policy_name"],
            "risk": "CRITICAL_WILDCARD_ADMIN"
        })
    else:
        print(f"[PASS] User '{user}' enforces scoped access rules.")

# Save violations to audit log
with open("iam_violations.json", "w") as out:
    json.dump(flagged_users, out, indent=2)

print("\n[COMPLETE] IAM policy audit complete. Violations logged to iam_violations.json")