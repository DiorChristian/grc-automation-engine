from datetime import datetime

def parse_hipaa_log(log_filename):
    total_events = 0
    denied_events = 0
    allowed_events = 0
    flagged_roles = []

    try:
        with open(log_filename, "r") as log_file:
            lines = log_file.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            total_events += 1
            
            if "[DENIED]" in line:
                denied_events += 1
                if "Role '" in line:
                    role = line.split("Role '")[1].split("'")[0]
                    flagged_roles.append(role)
            elif "[ALLOWED]" in line:
                allowed_events += 1

        failure_rate = (denied_events / total_events * 100) if total_events > 0 else 0.0

        report = f"""--- HIPAA COMPLIANCE AUDIT REPORT ---
Generated On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Source Log: {log_filename}

--- SUMMARY METRICS ---
Total Inspected Events: {total_events}
Allowed Accesses: {allowed_events}
Security Violations (DENIED): {denied_events}
Non-Compliance Rate: {failure_rate:.1f}%

--- FLAGGED ROLES ---
Roles Triggering Alerts: {set(flagged_roles)}
-------------------------------------
"""
        print(report)
        
        with open("audit_summary.txt", "w") as summary_file:
            summary_file.write(report)
            
        print("[+] Audit summary successfully saved to 'audit_summary.txt'")

        # --- AUTOMATED NIST THRESHOLD ALERT ---
        ALERT_THRESHOLD = 20.0  # 20% failure threshold
        if failure_rate > ALERT_THRESHOLD:
            alert_payload = (
                f"CRITICAL COMPLIANCE ALERT\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Control Triggered: NIST SP 800-53 AU-6\n"
                f"Failure Rate: {failure_rate:.1f}% (Exceeds {ALERT_THRESHOLD}% threshold)\n"
                f"Action Required: Immediate incident review for flagged roles: {set(flagged_roles)}\n"
            )
            with open("CRITICAL_NIST_ALERT.txt", "w") as alert_file:
                alert_file.write(alert_payload)
            print(f"[!] CRITICAL: Failure rate exceeds {ALERT_THRESHOLD}%! 'CRITICAL_NIST_ALERT.txt' generated.")

    except FileNotFoundError:
        print(f"[!] Error: The log file '{log_filename}' was not found.")

parse_hipaa_log("hipaa_audit.log")