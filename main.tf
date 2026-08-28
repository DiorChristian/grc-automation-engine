# 1. Create the Dead Letter Queue (DLQ) for quarantined/failed events
resource "aws_sqs_queue" "nist_sentinel_dlq" {
  name                      = "nist-sentinel-dead-letter-queue"
  message_retention_seconds = 1209600 # Retains failed messages for 14 days for inspection
  kms_master_key_id         = "alias/aws/sqs"
}

# 2. Create the Main SQS Queue and link it to the DLQ via Redrive Policy
resource "aws_sqs_queue" "nist_sentinel_main" {
  name                       = "nist-sentinel-main-queue"
  visibility_timeout_seconds = 300
  kms_master_key_id          = "alias/aws/sqs"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.nist_sentinel_dlq.arn
    maxReceiveCount     = 3 # Routes to DLQ after 3 failed attempts
  })
}

# 3. Grant Lambda permissions to read from the Main Queue
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.nist_sentinel_main.arn
  function_name    = aws_lambda_function.remediation_handler.arn
  batch_size       = 10
}

# 4. IAM Role for the Remediation Lambda Executor
resource "aws_iam_role" "lambda_execution_role" {
  name = "NISTCloudSentinelLambdaExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach basic execution policy and SQS poll permissions
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_poll" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}

# 5. The Remediation Lambda Function
resource "aws_lambda_function" "remediation_handler" {
  filename      = "lambda_payload.zip" 
  function_name = "nist-sentinel-remediation-processor"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "guardrail_engine.lambda_handler"
  runtime       = "python3.10"
  timeout       = 300
}