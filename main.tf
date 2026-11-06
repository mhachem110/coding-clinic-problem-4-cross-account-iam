provider "aws" {
  region = var.region
}

locals {
  object_arns = [for bucket in var.bucket_arns : "${bucket}/*"]
}

resource "aws_iam_role" "this" {
  name = var.role_name

  # Only the named account may assume this role, and it must provide the external ID.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${var.trusted_account_id}:root"
      }
      Action = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "sts:ExternalId" = var.external_id
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "s3_read" {
  name = "${var.role_name}-s3-read"
  role = aws_iam_role.this.id

  # Keep permissions narrow: list only the named buckets and read their objects.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = var.bucket_arns
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = local.object_arns
      }
    ]
  })
}

