output "role_arn" {
  description = "Role ARN for the trusted CI account to assume."
  value       = aws_iam_role.this.arn
}

