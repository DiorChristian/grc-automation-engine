from datetime import datetime

# Healthcare Role-Permission Matrix (HIPAA ePHI Access)
ROLE_PERMISSIONS = {
    "doctor": ["view_ephi", "update_patient_notes"],
    "nurse": ["view_ephi", "administer_meds"],
    "billing": ["view_invoices", "process_payment"],
    "admin": ["manage_schedules", "delete_patient_record"]
}

def verify_access(user_role, requested_action):
    # Cleaning inputs
    user_role = str(user_role).lower().strip()
    requested_action = str(requested_action).lower().strip()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check permissions
    allowed_actions = ROLE_PERMISSIONS.get(user_role, [])
    
    if requested_action in allowed_actions:
        print(f"[{timestamp}] [ALLOWED] Role '{user_role}' performed '{requested_action}'.")
        return True
    else:
        status_msg = f"[{timestamp}] [DENIED] ALERT: Role '{user_role}' attempted unauthorized action '{requested_action}'!"
        print(status_msg)
        
        # Write to audit log
        with open("hipaa_audit.log", "a") as log_file:
            log_file.write(status_msg + "\n")
            
        return False

# Test Run
print("--- RUNNING HEALTHCARE SECURITY CHECKS ---")
verify_access(" Doctor ", "view_ephi ")           # Test 1
verify_access("billing", "view_ephi")             # Test 2
verify_access("receptionist", "view_invoices")    # Test 3