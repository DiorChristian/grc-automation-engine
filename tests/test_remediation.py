import pytest
import json
from remediation_engine import auto_remediate_s3_bucket

def test_non_compliant_s3_bucket_remediation():
    """Test that a non-compliant payload is fully remediated and NIST violations cleared."""
    payload = {
        "resource_id": "s3-test-bucket-01",
        "resource_type": "AWS::S3::Bucket",
        "public_access_block": False,
        "encryption_enabled": False,
        "nist_controls_violated": ["AC-3", "SC-28"],
        "environment": "staging"
    }
    
    result = auto_remediate_s3_bucket(payload)
    
    assert result["public_access_block"] is True
    assert result["encryption_enabled"] is True
    assert result["status"] == "REMEDIATED_COMPLIANT"
    assert len(result["nist_controls_violated"]) == 0
    assert "audit_log" in result
    assert result["audit_log"]["nist_au_control"] == "AU-2 / AU-3"

def test_already_compliant_s3_bucket():
    """Test that an already compliant payload remains untouched."""
    payload = {
        "resource_id": "s3-secure-bucket-99",
        "resource_type": "AWS::S3::Bucket",
        "public_access_block": True,
        "encryption_enabled": True,
        "nist_controls_violated": [],
        "environment": "production"
    }
    
    result = auto_remediate_s3_bucket(payload)
    
    assert result["public_access_block"] is True
    assert result["encryption_enabled"] is True
    assert "audit_log" not in result  # No remediation triggered
