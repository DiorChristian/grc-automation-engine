import json

# Load audit findings from disk
try:
    with open("s3_incident_report.json", "r") as f:
        s3_incidents = json.load(f)
except FileNotFoundError:
    s3_incidents = []

print("[ALERT ENGINE STARTED] Packaging security findings for Webhook dispatch...\n")

webhook_payloads = []

for incident in s3_incidents:
    # Map raw technical findings to NIST 800-53 and SOC 2 Controls
    payload = {
        "event_type": "CLOUD_SECURITY_ALERT",
        "asset": incident["bucket_name"],
        "severity": "CRITICAL",
        "framework_mappings": {
            "NIST_800_53": "AC-3 Access Enforcement / SC-7 Boundary Protection",
            "SOC_2": "CC6.1 Logical Access Security / CC6.3 Least Privilege"
        },
        "violations_detected": incident["violations"],
        "action_required": "Automated containment script triggered via s3_remediator.py"
    }
    
    webhook_payloads.append(payload)
    print(f"[PACKAGED] Webhook payload generated for '{incident['bucket_name']}'")

# Save formatted outbound webhook notifications
with open("webhook_alerts.json", "w") as out:
    json.dump(webhook_payloads, out, indent=2)

print("\n[COMPLETE] 100% of findings converted to SOC 2 / NIST webhook alerts in webhook_alerts.json")