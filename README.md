# Problem 4: Cross-account IAM role

## What it does

Terraform defines a role that a named CI account can assume only when it supplies an external ID. The attached policy grants only `s3:ListBucket` and `s3:GetObject` on named bucket ARNs. A small Python checker validates the Terraform plan before deployment and rejects public trust, wildcard resources, or actions outside that allowlist.

See [`DESIGN.md`](DESIGN.md) for the trust boundary and policy validation flow.

## Files

- `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`: reusable Terraform role and least-privilege policy.
- `validate_iam.py`: checks the trust policy and permissions in a Terraform JSON plan.
- `fixtures/pass-plan.json`, `fixtures/fail-plan.json`: offline plan examples.
- `tests/test_validate_iam.py`: tests safe and unsafe policy plans.
- `.gitignore`: excludes Terraform state, plans, and provider downloads.

## Demo

```bash
python validate_iam.py fixtures/pass-plan.json \
  --trusted-account-id 111111111111 --external-id clinic-demo-2026
python validate_iam.py fixtures/fail-plan.json \
  --trusted-account-id 111111111111 --external-id clinic-demo-2026
python -m unittest discover -s tests -v
```

The first command passes. The second rejects the wildcard trust and `s3:*` permission. In a real workflow, use `terraform show -json tfplan > plan.json` and run the validator before `terraform apply`.

