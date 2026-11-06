import json
import unittest
from pathlib import Path

from validate_iam import check_plan


FIXTURES = Path(__file__).parents[1] / "fixtures"


class CrossAccountIamTests(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text())

    def test_safe_plan_passes(self):
        self.assertEqual(check_plan(self.load("pass-plan.json"), "111111111111", "clinic-demo-2026"), [])

    def test_public_trust_and_wildcard_policy_fail(self):
        problems = check_plan(self.load("fail-plan.json"), "111111111111", "clinic-demo-2026")
        self.assertGreaterEqual(len(problems), 3)
        self.assertTrue(any("trust" in problem for problem in problems))
        self.assertTrue(any("wildcard" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()

