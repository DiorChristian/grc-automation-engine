from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# Configure automated logging to write to a file
logging.basicConfig(
    filename='compliance_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route("/")
def home():
    return "GRC Automation Engine is running!"

@app.route("/audit/password", methods=["POST"])
def audit_password():
    data = request.get_json() or {}
    password = data.get("password", "")

    min_length = 12
    has_number = any(char.isdigit() for char in password)

    if len(password) >= min_length and has_number:
        result = {
            "status": "PASS",
            "message": "Password meets baseline security standards (NIST SP 800-63B).",
            "compliant": True
        }
        # Record successful audit event to log file
        logging.info("AUDIT PASS: Password meets NIST SP 800-63B guidelines.")
    else:
        result = {
            "status": "FAIL",
            "message": "Password violates policy: Must be at least 12 characters long and contain a number.",
            "compliant": False
        }
        # Record failed audit event to log file
        logging.warning("AUDIT FAIL: Password policy violation detected.")

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)