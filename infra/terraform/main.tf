provider "aws" {
  region = "us-east-1"
}

# 1. The "Brain" - SQS Queue
resource "aws_sqs_queue" "spot_queue" {
  name                      = "spot-hopping-queue"
  message_retention_seconds = 86400 # 1 day
  visibility_timeout_seconds = 60   # Time for worker to process
}

# 2. IAM Role for Spot Instances
resource "aws_iam_role" "spot_instance_role" {
  name = "spot-hopping-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attach Policy to allow SQS & Logging
resource "aws_iam_role_policy" "spot_instance_policy" {
  name = "spot-hopping-policy"
  role = aws_iam_role.spot_instance_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:ChangeMessageVisibility",
          "sqs:GetQueueUrl",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.spot_queue.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "spot_profile" {
  name = "spot-hopping-profile"
  role = aws_iam_role.spot_instance_role.name
}

output "queue_url" {
  value = aws_sqs_queue.spot_queue.id
}
