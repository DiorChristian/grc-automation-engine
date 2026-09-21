import boto3
import os
import logging
import json
from datetime import datetime

# Initialize AWS clients ☁️
sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

def validate_payload(msg):
    """
    🛡️ Pre-validation check to ensure required compliance fields exist.
    """
    body = msg.get('body', {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return False
    
    required_keys = ['control_id', 'event_type', 'timestamp']
    return all(key in body for key in required_keys)

def handle_dlq_and_worm(message, bucket_name, dlq_url):
    """
    🔒 Captures forensic snapshot into WORM vault and pushes to DLQ.
    """
    try:
        body_content = message['body'] if isinstance(message['body'], str) else json.dumps(message['body'])
        sqs.send_message(QueueUrl=dlq_url, MessageBody=body_content)
        
        snapshot_key = f"forensic_vault/failure_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(body_content)}.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=snapshot_key,
            Body=json.dumps({
                "error_reason": "Exhausted batch retries (3 attempts) or pre-validation failure",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": message
            }),
            ContentType='application/json'
        )
        logging.info(f"📁 Forensic snapshot securely stored in WORM bucket: {snapshot_key}")
    except Exception as err:
        logging.error(f"⚠️ Failed to process DLQ/WORM fallback: {err}")

def send_to_tier_queue(messages, is_high_priority=False, retry_tracker=None):
    """
    📥 Batches up to 10 messages and sends them to the appropriate 
    high-priority or standard SQS queue with pre-validation, 3-attempt retry tracking,
    DLQ routing, and WORM vault forensic archiving.
    """
    if retry_tracker is None:
        retry_tracker = {}

    queue_url = os.getenv(
        'HIGH_PRIORITY_QUEUE_URL' if is_high_priority else 'STANDARD_QUEUE_URL'
    )
    dlq_url = os.getenv('DLQ_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/dlq')
    worm_bucket = os.getenv('WORM_VAULT_BUCKET', 'grc-worm-audit-vault')
    
    # Check if queue URL is missing or using placeholder text
    if not queue_url or "your-" in queue_url:
        logging.warning("⚠️ SQS Queue URL not configured or using placeholder. Skipping SQS dispatch.")
        return False

    valid_messages = []
    
    # Step 1: Pre-validation gate 🛡️
    for msg in messages:
        if not validate_payload(msg):
            logging.warning("❌ Pre-validation failed for payload. Routing directly to DLQ/WORM vault.")
            handle_dlq_and_worm(msg, worm_bucket, dlq_url)
            continue
        valid_messages.append(msg)

    batch_size = 10
    for i in range(0, len(valid_messages), batch_size):
        batch = valid_messages[i:i + batch_size]
        entries = []
        batch_mapping = {}

        for index, msg in enumerate(batch):
            entry_id = str(index)
            body_content = msg['body'] if isinstance(msg['body'], str) else json.dumps(msg['body'])
            entries.append({
                'Id': entry_id,
                'MessageBody': body_content,
                'MessageAttributes': {
                    'Priority': {
                        'DataType': 'String',
                        'StringValue': 'High' if is_high_priority else 'Standard'
                    }
                }
            })
            batch_mapping[entry_id] = msg
        
        try:
            response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
            
            # Step 2: Handle partial batch failures with 3-attempt threshold 🔄
            failed = response.get('Failed', [])
            if failed:
                for failure in failed:
                    failed_id = failure['Id']
                    failed_msg = batch_mapping[failed_id]
                    msg_key = str(hash(str(failed_msg)))
                    
                    current_retries = retry_tracker.get(msg_key, 0) + 1
                    retry_tracker[msg_key] = current_retries
                    
                    if current_retries <= 3:
                        logging.info(f"🔄 Retrying failed message (Attempt {current_retries}/3)...")
                        send_to_tier_queue([failed_msg], is_high_priority, retry_tracker)
                    else:
                        logging.error("🚨 Message failed after 3 retries. Sending to DLQ and WORM Vault.")
                        handle_dlq_and_worm(failed_msg, worm_bucket, dlq_url)

        except Exception as e:
            logging.error(f"❌ Failed to send message batch to SQS: {e}")
            for msg in batch:
                handle_dlq_and_worm(msg, worm_bucket, dlq_url)
    
    return True