# 1. READ LOG FILE & TRACK FAILURES
failed_counts = {}

with open("auth.log", "r") as log_file:
    for line in log_file:
        # Strip trailing newline and whitespace
        clean_line = line.strip()
        
        # Parse user and status (e.g. "user:dev_intern, status:FAILED")
        parts = clean_line.split(", ")
        user = parts[0].split(":")[1]
        status = parts[1].split(":")[1]

        # Step A: Count failed attempts
        if status == "FAILED":
            failed_counts[user] = failed_counts.get(user, 0) + 1

# 2. EVALUATE COMPLIANCE THRESHOLD (NIST Policy: Max 3 Failures)
THRESHOLD = 3

for user, count in failed_counts.items():
    if count >= THRESHOLD:
        print(f"[SECURITY ALERT] {user} exceeded failed attempt threshold: {count} failures!")
    else:
        print(f"[OK] {user} has {count} failed attempt(s).")