import boto3
import os
import logging

# Initialize the SQS client ☁️
sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION', 'us-east-1'))

def send_to_tier_queue(messages, is_high_priority=False):
    """
    Batches up to 10 messages and sends them to the appropriate 
    high-priority or standard SQS queue 📥 with error handling.
    """
    queue_url = os.getenv(
        'HIGH_PRIORITY_QUEUE_URL' if is_high_priority else 'STANDARD_QUEUE_URL'
    )
    
    # Check if queue URL is missing or using placeholder text
    if not queue_url or "your-" in queue_url:
        logging.warning("SQS Queue URL not configured or using placeholder. Skipping SQS dispatch.")
        return False

    batch_size = 10
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        entries = [
            {
                'Id': str(index),
                'MessageBody': msg['body'],
                'MessageAttributes': {
                    'Priority': {
                        'DataType': 'String',
                        'StringValue': 'High' if is_high_priority else 'Standard'
                    }
                }
            }
            for index, msg in enumerate(batch)
        ]
        
        try:
            sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
        except Exception as e:
            logging.error("Failed to send message batch to SQS: %s", e)
            pass
    
    return True