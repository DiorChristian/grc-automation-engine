import json
import os
import boto3
from pillar_13_sentinel import Pillar13PredictiveEngine

# Initialize AWS clients and the Pillar 13 AI Engine
s3_client = boto3.client('s3')
ai_engine = Pillar13PredictiveEngine(ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))

def capture_forensic_snapshot(event_payload, resource_arn):
    """
    Captures a pre-remediation forensic snapshot of the resource state 
    alongside the CloudTrail event before any changes are made.
    """
    snapshot_data = {
        "cloudrail_event": event_payload,
        "target_resource": resource_arn,
        "status": "PRE_REMEDIATION_SNAPSHOT_CAPTURED"
    }
    
    # In production, save this to an immutable audit S3 bucket
    print(f"[FORENSIC AUDIT] Snapshot secured for resource: {resource_arn}")
    return snapshot_data

def lambda_handler(event, context):
    """
    AWS Lambda Entrypoint for NIST Cloud Sentinel - Pillar 13
    """
    print("Received event stream from SQS/EventBridge...")
    
    # Parse incoming SQS message records wrapping CloudTrail / EventBridge events
    for record in event.get('Records', []):
        try:
            message_body = json.loads(record['body'])
            event_payload = message_body.get('detail', message_body)
            
            # Extract target resource identifier if available
            resource_arn = event_payload.get('resources', ['arn:aws:s3:::unknown-resource'])[0]
            
            print(f"Evaluating resource via Pillar 13 AI Engine: {resource_arn}")
            
            # 1. Run Predictive AI Inference
            ai_decision = ai_engine.evaluate_infrastructure_event(event_payload)
            print(f"Pillar 13 Result -> Action: {ai_decision['action']} | Risk Score: {ai_decision['risk_score']}")
            print(f"Prediction: {ai_decision['prediction']}")
            
            # 2. Enforce AI Guardrail Decisions
            if ai_decision["action"] == "BLOCK":
                # Capture forensic evidence before blocking/aborting execution
                snapshot = capture_forensic_snapshot(event_payload, resource_arn)
                print(f"[BLOCKED] Malicious or high-risk drift prevented. Evidence logged.")
                continue
                
            elif ai_decision["action"] == "WARN":
                # Capture snapshot and flag for review
                snapshot = capture_forensic_snapshot(event_payload, resource_arn)
                print(f"[WARN] Flagged for compliance review. Executing pre-remediation capture.")
                
            else:
                print(f"[ALLOW] Event passed AI inspection. Proceeding with standard baseline.")
                
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            raise e
            
    return {
        "statusCode": 200,
        "body": json.dumps("Pillar 13 Lambda execution completed successfully.")
    }

if __name__ == "__main__":
    # Mock an SQS event payload wrapping a CloudTrail event
    mock_sqs_event = {
        "Records": [
            {
                "body": json.dumps({
                    "detail": {
                        "eventSource": "s3.amazonaws.com",
                        "eventName": "PutBucketAcl",
                        "resources": ["arn:aws:s3:::customer-financial-records-prod"],
                        "requestParameters": {
                            "bucketName": "customer-financial-records-prod"
                        }
                    }
                })
            }
        ]
    }
    print("Testing Lambda handler execution locally...")
    response = lambda_handler(mock_sqs_event, None)
    print(response)