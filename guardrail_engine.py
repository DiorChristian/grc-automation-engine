import json
import os
import boto3
import requests

s3_client = boto3.client('s3')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def evaluate_and_route_drift(event_payload):
    """
    Evaluates JSON event payload risk tier.
    Tier 1: Low-risk, autonomous fix (e.g., S3 public access block).
    Tier 2: High-risk, destructive, requires human-in-the-loop validation.
    """
    risk_score = event_payload.get('ai_risk_score', 0)
    violation_type = event_payload.get('violation_type')
    resource_arn = event_payload.get('resource_arn')

    # Tier 1: Autonomous Remediation (Instant execution)
    if risk_score < 75 and violation_type == "S3_PUBLIC_ACCESS_OPEN":
        print(f"[*] Tier 1 Autonomous Fix: Remediating {resource_arn} immediately.")
        execute_autonomous_remediation(resource_arn)
        return {"status": "AUTO_REMEDIATED", "tier": 1}

    # Tier 2: High-Risk / Ambiguous - Pause and Trigger Human-in-the-Loop Slack Approval
    elif risk_score >= 75:
        print(f"[!] Tier 2 High-Risk Alert: Halting execution for {resource_arn}. Dispatching Slack webhook.")
        trigger_slack_approval_workflow(event_payload)
        return {"status": "PENDING_HUMAN_APPROVAL", "tier": 2}

def execute_autonomous_remediation(resource_arn):
    # Extracts bucket name and enforces public block via Boto3
    bucket_name = resource_arn.split(":::")[1]
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

def trigger_slack_approval_workflow(payload):
    """
    Fires an interactive Slack webhook with Approve/Deny buttons 
    for the on-call engineer before Boto3 destructive remediation triggers.
    """
    slack_message = {
        "text": f"🚨 *High-Risk Cloud Drift Detected!*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Resource:* `{payload.get('resource_arn')}`\n*Risk Score:* `{payload.get('ai_risk_score')}`\n*Action:* Requires manual approval to execute auto-remediation."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve Fix"},
                        "style": "primary",
                        "value": "approve_remediation"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Deny / Inspect"},
                        "style": "danger",
                        "value": "deny_remediation"
                    }
                ]
            }
        ]
    }
    
    if SLACK_WEBHOOK_URL:
        response = requests.post(SLACK_WEBHOOK_URL, json=slack_message)
        print(f"Slack Webhook dispatched. Status: {response.status_code}")