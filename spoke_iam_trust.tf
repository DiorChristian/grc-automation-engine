# Spoke Account IAM Role that the Central Hub assumes for remediation
resource "aws_iam_role" "spoke_remediation_executor" {
  name = "NISTCloudSentinelSpokeExecutor"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.security_hub_account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:PrincipalTag/Environment" = ["Production", "Staging", "Development"]
          }
        }
      }
    ]
  })
}

# Attach the necessary auditing/remediation permissions to the spoke role
resource "aws_iam_role_policy_attachment" "spoke_execution_policy" {
  role       = aws_iam_role.spoke_remediation_executor.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}