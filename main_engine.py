import subprocess
import sys

print("==================================================")
print("   GRC AUTOMATION ENGINE - MASTER ORCHESTRATOR   ")
print("==================================================\n")

def run_step(script_name, description):
    print(f"[RUNNING STEP] {description} ({script_name})...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout.strip())
        
    if result.returncode != 0:
        print(f"\n[STEP FINDING] {script_name} returned Exit Code {result.returncode}.\n")
    else:
        print(f"[STEP PASSED] {script_name} returned Exit Code 0.\n")
        
    return result.returncode

# 1. Run S3 Storage Auditor
s3_status = run_step("s3_auditor.py", "Scanning S3 Storage Compliance")

if s3_status == 1:
    print("[PIPELINE TRIGGER] Storage violations detected! Launching Auto-Remediator...\n")
    run_step("s3_remediator.py", "Executing S3 Self-Healing Lockdown")
    print("[RE-VERIFYING] Re-checking S3 compliance baseline...")
    s3_status = run_step("s3_auditor.py", "S3 Post-Remediation Verification")

# 2. Run IAM Policy Auditor
iam_status = run_step("iam_auditor.py", "Auditing IAM Policies for Wildcard Exposure")

if iam_status == 1:
    print("[PIPELINE TRIGGER] Wildcard IAM policy detected! Dispatching alerts...\n")
    run_step("alert_engine.py", "Executing Incident Threat Alert Engine")

# 3. Run CloudTrail Runtime Log Auditor
cloudtrail_status = run_step("cloudtrail_auditor.py", "Parsing CloudTrail Runtime API Logs")

print("==================================================")
print("              SUMMARY PIPELINE REPORT             ")
print("==================================================")
print(f"S3 Storage Status         : {'COMPLIANT (0)' if s3_status == 0 else 'NON-COMPLIANT (' + str(s3_status) + ')'}")
print(f"IAM Policy Status         : {'COMPLIANT (0)' if iam_status == 0 else 'VIOLATIONS DETECTED (' + str(iam_status) + ')'}")
print(f"CloudTrail Runtime Audit  : {'COMPLIANT (0)' if cloudtrail_status == 0 else 'UNAUTHORIZED API CALLS DETECTED (' + str(cloudtrail_status) + ')'}")

# Circuit breaker exit code
if s3_status == 0 and iam_status == 0 and cloudtrail_status == 0:
    print("\n[PIPELINE SUCCESS] All security controls compliant. Exiting with status 0.")
    sys.exit(0)
else:
    print("\n[PIPELINE ALERT] Compliance findings logged. Circuit breaker activated (Exit Status 1).")
    sys.exit(1)