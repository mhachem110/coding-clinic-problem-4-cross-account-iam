#!/usr/bin/env python3
"""Validate the trust and permissions in a Terraform IAM plan."""

import argparse
import json
import sys
from pathlib import Path


ALLOWED_ACTIONS = {"s3:ListBucket", "s3:GetObject"}


def as_list(value):
    return value if isinstance(value, list) else [value]


def parse_policy(value):
    if not isinstance(value, str):
        raise ValueError("policy is unknown before apply")
    policy = json.loads(value)
    statements = policy.get("Statement", [])
    return statements if isinstance(statements, list) else [statements]


def check_plan(plan, trusted_account_id, external_id):
    """Return policy violations; an empty list means the plan is acceptable."""
    changes = plan.get("resource_changes")
    if not isinstance(changes, list):
        raise ValueError("expected a Terraform plan with resource_changes")

    problems = []
    role_found = False
    policy_found = False
    expected_principal = f"arn:aws:iam::{trusted_account_id}:root"

    for resource in changes:
        if resource.get("mode") != "managed":
            continue
        after = (resource.get("change") or {}).get("after") or {}
        if resource.get("type") == "aws_iam_role":
            role_found = True
            try:
                statements = parse_policy(after.get("assume_role_policy"))
            except (ValueError, json.JSONDecodeError) as exc:
                problems.append(f"{resource.get('address', 'role')}: invalid trust policy: {exc}")
                continue
            trusted = False
            for statement in statements:
                principal = (statement.get("Principal") or {}).get("AWS")
                condition = statement.get("Condition") or {}
                external_values = (condition.get("StringEquals") or {}).get("sts:ExternalId")
                if statement.get("Action") == "sts:AssumeRole" and expected_principal in as_list(principal) and external_id in as_list(external_values):
                    trusted = True
            if not trusted:
                problems.append(f"{resource.get('address', 'role')}: trust must require the account and external ID")

        if resource.get("type") == "aws_iam_role_policy":
            policy_found = True
            try:
                statements = parse_policy(after.get("policy"))
            except (ValueError, json.JSONDecodeError) as exc:
                problems.append(f"{resource.get('address', 'policy')}: invalid permission policy: {exc}")
                continue
            for statement in statements:
                actions = set(as_list(statement.get("Action")))
                resources = as_list(statement.get("Resource"))
                if statement.get("Effect") != "Allow":
                    problems.append(f"{resource.get('address', 'policy')}: permission statement must allow the intended read")
                if not actions <= ALLOWED_ACTIONS:
                    problems.append(f"{resource.get('address', 'policy')}: action outside the read-only allowlist")
                if "*" in resources:
                    problems.append(f"{resource.get('address', 'policy')}: wildcard resource is not allowed")

    if not role_found:
        problems.append("plan: aws_iam_role is missing")
    if not policy_found:
        problems.append("plan: aws_iam_role_policy is missing")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--trusted-account-id", required=True)
    parser.add_argument("--external-id", required=True)
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        problems = check_plan(plan, args.trusted_account_id, args.external_id)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print("PASS: cross-account IAM policy checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

