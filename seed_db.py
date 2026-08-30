from compliance_rag import ComplianceRAGEngine

def seed_comprehensive_frameworks():
    print("[*] Initializing comprehensive compliance RAG engine...")
    rag_engine = ComplianceRAGEngine()

    documents = [
        "Password complexity baseline standards: Passwords must be at least 12 characters long, contain a mix of uppercase and lowercase letters, numbers, and special characters, and avoid common dictionary words.",
        "Multi-factor authentication (MFA) requirements: MFA must be enforced for all administrative and remote user access points to cloud infrastructure and sensitive databases.",
        "Encryption standards: All data at rest must be encrypted using AES-256, and data in transit must use TLS 1.3 or higher.",
        "S3 Bucket Public Access Prohibition: Storage buckets containing electronic protected health information (ePHI) or sensitive customer data must have all public access blocked completely via bucket policies and ACLs.",
        "CloudTrail Logging Integrity: AWS CloudTrail must be enabled across all regions with log file validation and multi-region tracking turned on to ensure immutable audit trails.",
        "Access Control Principle of Least Privilege: IAM policies must strictly enforce least privilege access, prohibiting wildcard permissions ('*') on sensitive resource actions.",
        "Firewall and Security Group Restrictions: Network security groups must not expose administrative ports like SSH (22) or RDP (3389) directly to the public internet (0.0.0.0/0)."
    ]
    
    metadatas = [
        {"control_id": "IA-5(1)", "framework": "NIST SP 800-53"},
        {"control_id": "IA-2(1)", "framework": "NIST SP 800-53"},
        {"control_id": "SC-13", "framework": "NIST SP 800-53"},
        {"control_id": "164.312(a)(2)(iv)", "framework": "HIPAA Security Rule"},
        {"control_id": "AU-2", "framework": "NIST SP 800-53"},
        {"control_id": "AC-6", "framework": "NIST SP 800-53"},
        {"control_id": "SC-7", "framework": "PCI-DSS v4.0"}
    ]
    
    ids = [
        "control_ia_5_1", 
        "control_ia_2_1", 
        "control_sc_13", 
        "control_hipaa_encryption", 
        "control_au_2", 
        "control_ac_6", 
        "control_pci_sc_7"
    ]

    print("[*] Ingesting comprehensive compliance framework controls into ChromaDB...")
    rag_engine.ingest_controls(documents=documents, metadatas=metadatas, ids=ids)
    print(f"[+] Successfully embedded and stored {len(ids)} multi-framework controls locally!")

if __name__ == "__main__":
    seed_comprehensive_frameworks()