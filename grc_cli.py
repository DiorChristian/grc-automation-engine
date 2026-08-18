import sys
import subprocess

def run_command(script_name):
    print(f"\n==================================================")
    print(f"   RUNNING MODULE: {script_name}")
    print(f"==================================================")
    result = subprocess.run(["python3", script_name])
    if result.returncode != 0:
        print(f"\n[CLI ERROR] Module {script_name} failed or blocked execution.")
        return False
    return True

def main():
    print("**************************************************")
    print("      ENTERPRISE GRC AUTOMATION SUITE v1.0        ")
    print("**************************************************")
    
    # Execution Pipeline
    modules = [
        "s3_auditor.py",
        "iam_auditor.py",
        "cloudtrail_auditor.py",
        "alert_notifier.py",
        "compliance_gate.py"
    ]

    for module in modules:
        success = run_command(module)
        if not success:
            print("\n[MASTER GATE: BLOCKED] Pipeline halted due to compliance failure.")
            sys.exit(1)

    print("\n[MASTER GATE: PASSED] All GRC modules verified compliant.")
    sys.exit(0)

if __name__ == "__main__":
    main()