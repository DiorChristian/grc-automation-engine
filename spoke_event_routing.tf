variable "central_hub_event_bus_arn" {
  type        = string
  description = "ARN of the EventBus in the central Security Hub account"
}

# EventBridge Rule in Spoke Account to catch security/drift events
resource "aws_cloudwatch_event_rule" "spoke_drift_detector" {
  name        = "nist-sentinel-spoke-drift-rule"
  description = "Captures configuration drift and security findings locally"

  event_pattern = jsonencode({
    source      = ["aws.guardduty", "aws.config", "aws.s3"]
    detail-type = ["AWS API Call via CloudTrail", "GuardDuty Finding", "Config Rules Evaluation Change"]
  })
}

# Target pointing to the Central Security Hub Event Bus
resource "aws_cloudwatch_event_target" "forward_to_hub" {
  rule      = aws_cloudwatch_event_rule.spoke_drift_detector.name
  target_id = "SendToCentralSecurityHub"
  arn       = var.central_hub_event_bus_arn
  role_arn  = aws_iam_role.eventbridge_cross_account_publisher.arn
}

# IAM Role allowing Spoke EventBridge to publish to Hub EventBus
resource "aws_iam_role" "eventbridge_cross_account_publisher" {
  name = "NISTSentinelEventBridgePublisher"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "eventbridge_publish_policy" {
  role = aws_iam_role.eventbridge_cross_account_publisher.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "events:PutEvents"
      Resource = var.central_hub_event_bus_arn
    }]
  })
}