variable "security_hub_account_id" {
  type        = string
  description = "AWS Account ID of the central Security Hub orchestrator"
}

# IAM Role in Spoke Account that Central Hub assumes for auditing/remediation
resource "aws_iam_role" "spoke_remediation_executor" {
  name = "NISTCloudSentinelSpokeExecutor"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.security_hub_account_id}:root"
        }
        Condition = {
          StringEquals = {
            "aws:PrincipalTag/Environment" = ["Production", "Staging", "Development"]
          }
        }
      }
    ]
  })
}

# Attach least-privilege policy boundaries or specific GRC audit/remediation permissions
resource "aws_iam_role_policy_attachment" "spoke_execution_policy" {
  role       = aws_iam_role.spoke_remediation_executor.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit" # Or your custom least-privilege remediation policy
}