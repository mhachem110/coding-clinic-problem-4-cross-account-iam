variable "region" {
  description = "AWS region used by the provider. IAM is global, but the provider still needs a region."
  type        = string
  default     = "us-east-1"
}

variable "role_name" {
  description = "Name of the role assumed by the trusted CI account."
  type        = string
  default     = "ClinicReadOnlyRole"
}

variable "trusted_account_id" {
  description = "AWS account allowed to assume the role."
  type        = string
}

variable "external_id" {
  description = "Shared external ID required on every AssumeRole request."
  type        = string
  sensitive   = true
}

variable "bucket_arns" {
  description = "Specific S3 bucket ARNs the role can inspect."
  type        = list(string)
  default     = []
}

