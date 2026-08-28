import json
import sys

print("[CLOUDTRAIL AUDITOR STARTED] Parsing Runtime API Audit Logs...\n")

LOG_FILE = "cloudtrail_logs.json"

# High-risk security events that violate compliance baselines
CRITICAL_EVENTS = ["StopLogging", "DeleteSecurityGroup", "DeleteTrail", "PutBucketAcl"]

try:
    with open(LOG_FILE, "r") as f:
        events = json.load(f)
except Exception as e:
    print(f"[CRITICAL ERROR] Could not read CloudTrail logs: {str(e)}")
    sys.exit(2)

violations = []

for event in events:
    event_id = event.get("eventId", "UNKNOWN_EVT")
    event_name = event.get("eventName", "UNKNOWN_ACTION")
    user_identity = event.get("userIdentity", {})
    user_name = user_identity.get("userName", "UNKNOWN_USER")
    event_time = event.get("eventTime", "UNKNOWN_TIME")

    if event_name in CRITICAL_EVENTS:
        violation = {
            "eventId": event_id,
            "eventTime": event_time,
            "user": user_name,
            "unauthorizedAction": event_name,
            "riskLevel": "CRITICAL_COMPLIANCE_BREACH",
            "complianceControl": "NIST SP 800-53 AU-2 / SOC 2 CC6.8"
        }
        violations.append(violation)
        print(f"[VIOLATION DETECTED] User '{user_name}' performed unauthorized action '{event_name}' (ID: {event_id})")

with open("cloudtrail_violations.json", "w") as out:
    json.dump(violations, out, indent=2)

print("\n--------------------------------------------------")
if len(violations) > 0:
    print(f"[COMPLETED] Found {len(violations)} unauthorized runtime API event(s). Exiting with status 1.")
    sys.exit(1)
else:
    print("[COMPLETED] All runtime CloudTrail logs compliant. Exiting with status 0.")
    sys.exit(0)