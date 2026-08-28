import json
import sys

print("[CI/CD PIPELINE GATEKEEPER STARTED] Checking build safety status...\n")

# Load webhook alert payloads
try:
    with open("webhook_alerts.json", "r") as f:
        alerts = json.load(f)
except FileNotFoundError:
    alerts = []

critical_findings = [a for a in alerts if a.get("severity") == "CRITICAL"]

# Pipeline Decision Logic
if critical_findings:
    print(f"[BUILD BLOCKED] Found {len(critical_findings)} CRITICAL compliance violation(s)!")
    for item in critical_findings:
        print(f"  - Target Asset: {item['asset']}")
        print(f"  - Framework Violation: {item['framework_mappings']['SOC_2']}")
    
    print("\n[PIPELINE STATUS: FAILED] Deployment aborted. Non-compliant code rejected.")
    sys.exit(1)
else:
    print("[PIPELINE STATUS: PASSED] 0 critical compliance findings detected.")
    print("[DEPLOYING] Code approved for production release.")
    sys.exit(0)