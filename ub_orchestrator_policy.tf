variable "spoke_account_ids" {
  type        = list(string)
  description = "List of all AWS Spoke Account IDs"
}

# Policy allowing Central Security Hub Lambda/Service to assume spoke roles
resource "aws_iam_policy" "hub_cross_account_assume" {
  name        = "NISTCloudSentinelHubAssumePolicy"
  description = "Enables central orchestrator to assume roles across spoke accounts securely."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = [
          for acc_id in var.spoke_account_ids : "arn:aws:iam::${acc_id}:role/NISTCloudSentinelSpokeExecutor"
        ]
      }
    ]
  })
}