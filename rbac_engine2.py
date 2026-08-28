# 1. PERMISSION MATRIX
ASSIGNED_PERMISSIONS = {
    "doctor": ["read_ephi", "update_records"],
    "nurse": ["read_ephi"],
    "admin": ["read_ephi", "update_records", "delete_records", "manage_users"]
}

# 2. ACCESS EVALUATOR FUNCTION
def validate_access(user_role, requested_action):
    # Step 1: Input Sanitization (Clean both inputs)
    clean_role = user_role.strip().lower()
    clean_action = requested_action.strip().lower()

    # Step 2: Safe Dictionary Lookup (Use .get with [] fallback)
    user_perms = ASSIGNED_PERMISSIONS.get(clean_role, [])

    # Step 3: Authorization Decision Gate
    if clean_action in user_perms:
        print(f"[SUCCESS] Access granted to {clean_role} for {clean_action}")
        return True

    # Step 4: Handle Denial & Audit Logging
    alert = f"[ALERT] Unauthorized attempt by {clean_role} for {clean_action}"
    print(alert)

    # Step 5: Append to Log File ("a" mode)
    with open("access_audit.log", "a") as log_file:
        log_file.write(alert + "\n")

    return False

# 3. TEST EXECUTION
validate_access(" Doctor ", "READ_EPHI")
validate_access("nurse", "delete_records")
validate_access("pharmacist", "read_ephi")