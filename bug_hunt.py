# IAM ACCESS AUDITOR
ASSIGNED_PERMISSIONS = {
    "security_analyst": ["read_logs", "run_scans"],
    "compliance_officer": ["read_logs", "generate_reports"]
}

def evaluate_access_event(user_role, action_request):
    clean_role = user_role.strip().lower()
    clean_action = action_request.strip().lower()
    # Retrieve permissions
    user_perms = ASSIGNED_PERMISSIONS.get(clean_role, [])
    
    # Check authorization
    if clean_action in user_perms:
        print(f"[ALLOWED] {user_role} performed {action_request}")
        return True
    
    # Handle denial
    alert = f"[DENIED] {user_role} attempted {action_request}"
    print(alert)
    
    # Write to audit log
    with open("iam_violations.log", "a") as log_file:
        log_file.write(alert + "\n")
        
    return False

# Test Execution
evaluate_access_event(" Security_Analyst ", "read_logs")
evaluate_access_event("dev_intern", "run_scans")