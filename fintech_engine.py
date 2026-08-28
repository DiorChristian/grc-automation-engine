from datetime import datetime

# FinTech Role-Permission Matrix
ROLE_PERMISSIONS = {
    "teller": ["deposit", "withdraw_small"],
    "manager": ["deposit", "withdraw_small", "withdraw_large", "override_flag"],
    "auditor": ["view_ledger"],
    "trader": ["execute_trade", "view_market"]
}

def verify_access(user_role, requested_action):
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
        with open("fintech_audit.log", "a") as log_file:
            log_file.write(status_msg + "\n")
            
        return False

# Test Run
print("--- RUNNING FINTECH SECURITY CHECKS ---")
verify_access("teller", "DEPOSIT")        # Test 1: Should be ALLOWED, but gets DENIED
verify_access("teller", "withdraw_large")   # Test 2: DENIED (First violation)
verify_access("trader", "withdraw_large")   # Test 3: DENIED (Second violation)