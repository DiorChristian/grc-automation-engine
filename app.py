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
    return "GRC Automation Engine is running with Local RAG Compliance!"

@app.route("/audit/password", methods=["POST"])
def audit_password():
    data = request.get_json() or {}
    password = data.get("password", "")

    min_length = 12
    has_number = any(char.isdigit() for char in password)

    # Query local ChromaDB for exact regulatory compliance text
    rag_query_text = "Password complexity baseline standards and length requirements"
    compliance_standard = rag_engine.query_control(rag_query_text)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

