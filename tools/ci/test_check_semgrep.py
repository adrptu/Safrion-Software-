"""Regressões do falso verde: relatório vazio, análise parcial e inventário incompleto."""
import copy
from pathlib import Path
import tempfile
import unittest

from check_semgrep import VERSION, RULES, check_fixtures, check_scan, targets


class SemgrepEvidence(unittest.TestCase):
    def test_complete_scan(self):
        check_scan(self.report(), ["packages/domain/src/saldo.ts"])

    def report(self):
        return {"version": VERSION, "errors": [], "results": [],
                "skipped_rules": [], "time": {"fixpoint_timeouts": []},
                "paths": {"scanned": ["packages/domain/src/saldo.ts"]}}

    def test_partial_empty_and_finding_fail(self):
        for changes in ({"errors": [{}]}, {"paths": {"scanned": []}}, {"results": [{}]},
                        {"version": "old"}, {"results": None}, {"errors": None},
                        {"skipped_rules": [{}]}, {"time": {"fixpoint_timeouts": [{}]}},
                        {"paths": {"scanned": ["packages/domain/test/saldo.test.ts"]}}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                check_scan({**self.report(), **changes}, ["packages/domain/src/saldo.ts"])
        with self.assertRaises(ValueError):
            check_scan(self.report(), [])

    def fixtures(self):
        return {"config_missing_tests": [], "config_with_errors": [],
                "results": {"rule.yml": {"checks": {rule: {
                    "passed": True, "errors": [], "matches": {
                        "rule.ts": {"expected_lines": [1], "reported_lines": [1]}}}
                    for rule in RULES}}}}

    def test_fixtures_with_evidence(self):
        check_fixtures(self.fixtures())

    def test_empty_fixtures_are_not_success(self):
        for report in ({}, {**self.fixtures(), "results": {}},
                       {**self.fixtures(), "config_with_errors": ["error"]}):
            with self.subTest(report=report), self.assertRaises(ValueError):
                check_fixtures(report)

    def test_missing_rule_detection_or_negative_failure(self):
        for change in ({"passed": False}, {"errors": [{}]}, {"matches": {}},
                       {"matches": {"r.ts": {"expected_lines": [], "reported_lines": []}}},
                       {"matches": {"r.ts": {"expected_lines": [1], "reported_lines": [1, 2]}}}):
            report = copy.deepcopy(self.fixtures())
            report["results"]["rule.yml"]["checks"][sorted(RULES)[0]].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                check_fixtures(report)
        report = self.fixtures()
        del report["results"]["rule.yml"]["checks"][sorted(RULES)[0]]
        with self.assertRaises(ValueError):
            check_fixtures(report)

    def test_inventory_includes_ui_and_ignores_tests_and_build(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                targets(root)
            names = ["apps/web/next.config.ts", "apps/web/src/page.tsx", "packages/db/src/read.ts", "apps/web/dist/server.js",
                     "packages/db/test/sample.ts", ".semgrep/safrion.ts"]
            for name in names:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("")
            self.assertEqual(targets(root), names[:3])


if __name__ == "__main__":
    unittest.main()
