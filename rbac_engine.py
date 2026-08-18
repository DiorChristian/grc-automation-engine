from datetime import datetime

# 1. Role-Permission Matrix (Including Doctor)
ROLE_PERMISSIONS = {
    "admin": ["read_logs", "write_logs", "view_ephi", "delete_records"],
    "auditor": ["read_logs"],
    "developer": ["read_logs", "write_code"],
    "doctor": ["view_ephi", "read_logs"]
}

# 2. Gatekeeper Function with File Logging
def verify_access(user_role, requested_action):
    allowed_actions = ROLE_PERMISSIONS.get(user_role, [])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if requested_action in allowed_actions:
        print(f"[{timestamp}] [ALLOWED] Role '{user_role}' performed '{requested_action}'.")
        return True
    else:
        status_msg = f"[{timestamp}] [DENIED] ALERT: Role '{user_role}' attempted unauthorized action '{requested_action}'!"
        print(status_msg)
        
        # Write the security violation directly to disk
        with open("compliance_audit.log", "a") as log_file:
            log_file.write(status_msg + "\n")
            
        return False

# 3. Test Cases
print("--- RUNNING SECURITY CHECKS ---")
verify_access("admin", "view_ephi")
verify_access("developer", "view_ephi")
verify_access("doctor", "view_ephi")