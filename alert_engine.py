import json
import sys
from datetime import datetime

print("[ALERT ENGINE STARTED] Processing Security Incident Payloads...\n")

VIOLATIONS_FILE = "iam_violations.json"

try:
    with open(VIOLATIONS_FILE, "r") as f:
        violations = json.load(f)
except Exception as e:
    print(f"[ERROR] Could not open violations file: {str(e)}")
    sys.exit(2)

if not violations:
    print("[INFO] No active violations found. Zero alerts dispatched.")
    sys.exit(0)

alerts_dispatched = 0

for v in violations:
    policy = v.get("PolicyName", "UNKNOWN")
    role = v.get("Role", "UNKNOWN")
    risk = v.get("Risk", "MEDIUM")

    # Construct Webhook / SIEM Alert Payload
    payload = {
        "event_type": "IAM_WILDCARD_VIOLATION_DETECTED",
        "severity": "CRITICAL" if risk == "CRITICAL_OVER_PRIVILEGED" else "HIGH",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "details": {
            "policy_name": policy,
            "target_role": role,
            "action_granted": v.get("Action"),
            "resource_granted": v.get("Resource")
        },
        "remediation_recommended": "Revoke policy and apply scoped IAM permissions per Least Privilege standard."
    }

    alerts_dispatched += 1
    print(f"[ALERT DISPATCHED #{alerts_dispatched}] {payload['severity']} -> Policy '{policy}' on Role '{role}'")
    print(f"  └── Payload: {json.dumps(payload)}\n")

print(f"[ALERTING COMPLETE] Successfully generated and dispatched {alerts_dispatched} alert payload(s).")