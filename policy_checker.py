import json

# 1. READ & PARSE JSON CONFIG
with open("cloud_config.json", "r") as config_file:
    buckets = json.load(config_file)

# 2. AUDIT COMPLIANCE CONTROLS
for bucket in buckets:
    # Use safe .get() fallback for each key
    name = bucket.get("bucket_name", "UNKNOWN")
    is_public = bucket.get("is_public", False)
    encryption = bucket.get("encryption", "NONE")

    # Control #1 Check: Public Access Limit
    if is_public:
        print(f"[CRITICAL] {name} is PUBLICLY accessible!")

    # Control #2 Check: Encryption Requirement
    if encryption == "NONE":
        print(f"[WARNING] {name} is missing encryption at rest!")

    # Compliant State Check
    if not is_public and encryption != "NONE":
        print(f"[PASS] {name} is fully compliant.")