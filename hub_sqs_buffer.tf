# Dead Letter Queue for failed payloads (The "Six Flags Fight" Quarantine Lane)
resource "aws_sqs_queue" "sentinel_dlq" {
  name                      = "nist-sentinel-dlq.fifo"
  fifo_queue                = true
  content_based_deduplication = true
  message_retention_seconds = 1209600 # Retain failed payloads for 14 days for forensic review
}

# Main Ordered SQS Queue
resource "aws_sqs_queue" "sentinel_main_queue" {
  name                        = "nist-sentinel-main-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = 300 # Matches Lambda max execution window

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.sentinel_dlq.arn
    maxReceiveCount     = 3 # 3 tries before sending to DLQ
  })
}

# Central EventBus Rule to route incoming cross-account events straight into SQS
resource "aws_cloudwatch_event_bus" "central_hub_bus" {
  name = "nist-sentinel-central-bus"
}

resource "aws_cloudwatch_event_rule" "hub_ingest_rule" {
  event_bus_name = aws_cloudwatch_event_bus.central_hub_bus.name
  name           = "ingest-all-spoke-drift-events"
  event_pattern = jsonencode({
    source = [{ "prefix" = "aws." }]
  })
}

resource "aws_cloudwatch_event_target" "sqs_target" {
  event_bus_name = aws_cloudwatch_event_bus.central_hub_bus.name
  rule           = aws_cloudwatch_event_rule.hub_ingest_rule.name
  target_id      = "EnqueueToSQS"
  arn            = aws_sqs_queue.sentinel_main_queue.arn
}
