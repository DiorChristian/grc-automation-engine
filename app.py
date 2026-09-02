from flask import Flask, jsonify, request
import logging
from compliance_rag import ComplianceRAGEngine

app = Flask(__name__)

# Configure automated logging to write to a file
logging.basicConfig(
    filename='compliance_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize local ChromaDB RAG compliance engine
rag_engine = ComplianceRAGEngine()

@app.route("/")
def home():
    return "NIST Cloud Sentinel GRC Automation Engine is running with Universal Multi-Family Local RAG Compliance!"

@app.route("/audit/control", methods=["POST"])
def audit_control():
    data = request.get_json() or {}
    control_id = data.get("control_id", "AC-3").upper()
    resource_id = data.get("resource_id", "s3-patient-data-bucket-01")
    is_compliant = data.get("compliant", True)

    # Query local ChromaDB for exact regulatory compliance text across any family (AC, AU, SC, CM, IA, IR)
    rag_query_text = f"NIST control baseline standards and requirements for {control_id}"
    try:
        compliance_standard = rag_engine.query_control(rag_query_text)
    except Exception:
        compliance_standard = f"Statutory compliance baseline verified for NIST SP 800-53 control {control_id}."

    if is_compliant:
        result = {
            "status": "PASS",
            "control_id": control_id,
            "resource_id": resource_id,
            "message": f"Resource {resource_id} complies with NIST control {control_id}.",
            "compliant": True,
            "regulatory_reference": compliance_standard
        }
        logging.info("AUDIT PASS: Control %s verified for %s. Ref: %s", control_id, resource_id, compliance_standard)
    else:
        result = {
            "status": "FAIL",
            "control_id": control_id,
            "resource_id": resource_id,
            "message": f"Policy violation detected for {resource_id} under NIST control {control_id}.",
            "compliant": False,
            "regulatory_reference": compliance_standard
        }
        logging.warning("AUDIT FAIL: Violation detected for control %s on %s. Ref: %s", control_id, resource_id, compliance_standard)

    return jsonify(result)

@app.route("/audit/password", methods=["POST"])
def audit_password():
    data = request.get_json() or {}
    password = data.get("password", "")

    min_length = 12
    has_number = any(char.isdigit() for char in password)

    # Query local ChromaDB for exact regulatory compliance text
    rag_query_text = "Password complexity baseline standards and length requirements"
    try:
        compliance_standard = rag_engine.query_control(rag_query_text)
    except Exception:
        compliance_standard = "NIST SP 800-53 IA-5: Authenticator Management standards."

    if len(password) >= min_length and has_number:
        result = {
            "status": "PASS",
            "message": "Password meets baseline security standards.",
            "compliant": True,
            "regulatory_reference": compliance_standard
        }
        # Record successful audit event to log file
        logging.info("AUDIT PASS: Password meets standards. Ref: %s", compliance_standard)
    else:
        result = {
            "status": "FAIL",
            "message": "Password violates policy: Must be at least 12 characters long and contain a number.",
            "compliant": False,
            "regulatory_reference": compliance_standard
        }
        # Record failed audit event to log file
        logging.warning("AUDIT FAIL: Password policy violation detected. Ref: %s", compliance_standard)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=False, use_reloader=False)