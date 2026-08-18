import json
import sys

print("[CLOUDTRAIL AUDITOR STARTED] Parsing audit logs with chaos handling...\n")

CRITICAL_EVENTS = ["DeleteTrail", "StopLogging", "PutBucketPolicy", "AttachUserPolicy"]
LOG_FILE = "corrupted_cloudtrail.json"  # Pointing to chaos test payload

try:
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)
except FileNotFoundError:
    print(f"[CRITICAL ERROR] File '{LOG_FILE}' not found.")
    sys.exit(2)
except json.JSONDecodeError:
    print(f"[CRITICAL ERROR] File '{LOG_FILE}' contains invalid JSON formatting.")
    sys.exit(2)

suspicious_activities = []
execution_error = False

for entry in logs:
    try:
        # Defensive extraction handling null/missing structures
        event_name = entry.get("eventName")
        
        user_identity = entry.get("userIdentity") or {}
        user = user_identity.get("userName", "Unknown_User")
        
        response_elements = entry.get("responseElements") or {}
        status = response_elements.get("status", "Unknown_Status")
        
        ip = entry.get("sourceIPAddress", "0.0.0.0")

        # Evaluate risk conditions
        if (event_name and event_name in CRITICAL_EVENTS) or status == "AccessDenied":
            finding = {
                "eventId": entry.get("eventId", "UNKNOWN_EVT"),
                "actor": user,
                "action": event_name or "UNSPECIFIED_ACTION",
                "status": status,
                "ip_address": ip,
                "risk_level": "CRITICAL" if event_name == "DeleteTrail" else "HIGH"
            }
            suspicious_activities.append(finding)
            print(f"[FLAGGED EVENT] Actor '{user}' executed '{event_name}' (Status: {status})")

    except Exception as e:
        print(f"[NON-FATAL ERROR] Failed to process log entry {entry.get('eventId')}: {str(e)}")
        execution_error = True

# Write out violation evidence
with open("cloudtrail_violations.json", "w") as out:
    json.dump(suspicious_activities, out, indent=2)

if execution_error:
    print("\n[COMPLETED WITH ERRORS] Log parsing finished with non-fatal item errors.")
    sys.exit(2)
elif len(suspicious_activities) > 0:
    print(f"\n[COMPLETED] Found {len(suspicious_activities)} security finding(s). Exiting with status 1.")
    sys.exit(1)
else:
    print("\n[COMPLETED] 0 security findings. Exiting with status 0.")
    sys.exit(0)