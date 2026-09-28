import contextlib
import copy
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
import yaml
from azure.core.exceptions import ClientAuthenticationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import _fabric
import rules_engine
import validate


GROUP_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


class GraphGroupLookupTests(unittest.TestCase):
    def setUp(self):
        self.response = Mock(status_code=200)
        self.response.json.return_value = {"id": GROUP_ID}
        self.get = self.enterContext(patch("_fabric.requests.get", return_value=self.response))
        self.token = self.enterContext(patch("_fabric.token", return_value="test-token"))

    def test_requests_only_id_with_graph_token(self):
        self.assertTrue(_fabric.graph_group_exists(GROUP_ID))
        self.token.assert_called_once_with(_fabric.GRAPH_SCOPE)
        self.get.assert_called_once_with(
            f"https://graph.microsoft.com/v1.0/groups/{GROUP_ID}",
            headers={"Authorization": "Bearer test-token"},
            params={"$select": "id"},
            timeout=30,
        )

    def test_group_id_comparison_is_case_insensitive(self):
        self.response.json.return_value = {"id": GROUP_ID.upper()}
        self.assertTrue(_fabric.graph_group_exists(GROUP_ID))

    def test_only_404_means_not_found(self):
        self.response.status_code = 404
        self.assertFalse(_fabric.graph_group_exists(GROUP_ID))
        self.response.json.assert_not_called()

    def test_http_errors_do_not_mean_not_found_or_expose_response_body(self):
        self.response.text = "private-response-content"
        for status in (401, 403, 429, 500, 503):
            with self.subTest(status=status):
                self.response.status_code = status
                with self.assertRaisesRegex(_fabric.GraphGroupLookupError, f"HTTP {status}") as error:
                    _fabric.graph_group_exists(GROUP_ID)
                self.assertNotIn("private-response-content", str(error.exception))

    def test_authentication_error_is_explicit_and_sanitized(self):
        self.token.side_effect = ClientAuthenticationError("private-auth-details")
        with self.assertRaisesRegex(_fabric.GraphGroupLookupError, "authenticate") as error:
            _fabric.graph_group_exists(GROUP_ID)
        self.assertNotIn("private-auth-details", str(error.exception))
        self.get.assert_not_called()

    def test_request_failures_are_explicit_and_sanitized(self):
        for error in (requests.Timeout("private-details"), requests.ConnectionError("private-details")):
            with self.subTest(error=type(error).__name__):
                self.get.side_effect = error
                with self.assertRaisesRegex(_fabric.GraphGroupLookupError, "request failed") as caught:
                    _fabric.graph_group_exists(GROUP_ID)
                self.assertNotIn("private-details", str(caught.exception))

    def test_invalid_success_payloads_are_not_accepted(self):
        for body in (None, [], {}, {"id": None}, {"id": 42}, {"id": "different-group"}):
            with self.subTest(body=body):
                self.response.json.return_value = body
                with self.assertRaisesRegex(_fabric.GraphGroupLookupError, "requested group ID"):
                    _fabric.graph_group_exists(GROUP_ID)
        self.response.json.side_effect = ValueError("private-response-content")
        with self.assertRaisesRegex(_fabric.GraphGroupLookupError, "invalid JSON"):
            _fabric.graph_group_exists(GROUP_ID)


class LiveGroupValidationTests(unittest.TestCase):
    def setUp(self):
        sample = rules_engine.REPO_ROOT / "workspaces" / "pt-nlyt-sample-ndf-dev-hello1.yaml"
        self.manifest = rules_engine.load_yaml(sample)
        self.manifest["owners"][0]["identifier"] = GROUP_ID
        self.policy = rules_engine.load_policy()
        self.schema = rules_engine.load_schema()

    def test_optional_group_name_is_not_required(self):
        self.assertNotIn("groupName", self.manifest["owners"][0])
        self.assertEqual(rules_engine.validate_schema(self.manifest, self.schema), [])

    def test_offline_mode_does_not_query_graph(self):
        for setting in (None, "", "false"):
            with self.subTest(setting=setting), patch.dict(os.environ):
                if setting is None:
                    os.environ.pop("LIVE_CHECKS", None)
                else:
                    os.environ["LIVE_CHECKS"] = setting
                with patch("_fabric.graph_group_exists") as lookup:
                    result = rules_engine.validate_manifest(self.manifest, self.policy, self.schema)
                lookup.assert_not_called()
                self.assertTrue(result.passed)
                self.assertFalse(any(f.rule_id == "owner-groups-exist" for f in result.findings))

    def test_enabled_checks_report_success_missing_and_failure(self):
        cases = (
            (True, True, "info", "HTTP 200"),
            (False, False, "block", "HTTP 404"),
            (_fabric.GraphGroupLookupError("HTTP 403"), False, "block", "HTTP 403"),
            (_fabric.GraphGroupLookupError("request failed"), False, "block", "request failed"),
        )
        for outcome, passed, severity, message in cases:
            with self.subTest(outcome=outcome), patch.dict(os.environ, LIVE_CHECKS="true"):
                with patch("_fabric.graph_group_exists") as lookup:
                    if isinstance(outcome, Exception):
                        lookup.side_effect = outcome
                    else:
                        lookup.return_value = outcome
                    result = rules_engine.validate_manifest(self.manifest, self.policy, self.schema)
                lookup.assert_called_once_with(GROUP_ID)
                self.assertEqual(result.passed, passed)
                finding, = [f for f in result.findings if f.rule_id == "owner-groups-exist"]
                self.assertEqual(finding.severity, severity)
                self.assertIn(message, finding.message)

    def test_missing_dependencies_block_live_checks(self):
        with patch.dict(os.environ, LIVE_CHECKS="true"), patch.dict(sys.modules, {"_fabric": None}):
            result = rules_engine.validate_manifest(self.manifest, self.policy, self.schema)
        self.assertFalse(result.passed)
        self.assertTrue(any(
            f.rule_id == "owner-groups-exist" and f.severity == "block"
            and "dependencies" in f.message for f in result.findings
        ))

    def test_all_groups_checked_after_one_lookup_fails(self):
        second = copy.deepcopy(self.manifest["owners"][0])
        second["identifier"] = "11111111-2222-3333-4444-555555555555"
        self.manifest["owners"].append(second)
        with patch.dict(os.environ, LIVE_CHECKS="true"), patch(
            "_fabric.graph_group_exists",
            side_effect=[_fabric.GraphGroupLookupError("HTTP 403"), True],
        ) as lookup:
            result = rules_engine.validate_manifest(self.manifest, self.policy, self.schema)
        self.assertEqual(lookup.call_count, 2)
        self.assertFalse(result.passed)
        self.assertEqual(
            [f.severity for f in result.findings if f.rule_id == "owner-groups-exist"],
            ["block", "info"],
        )

    def test_cli_exit_and_both_reports_reflect_live_outcome(self):
        for outcome, code, message in (
            (True, 0, "HTTP 200"),
            (False, 1, "HTTP 404"),
            (_fabric.GraphGroupLookupError("HTTP 403"), 1, "HTTP 403"),
        ):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fixture = root / "workspace.yaml"
                fixture.write_text(yaml.safe_dump(self.manifest), encoding="utf-8")
                summary = root / "summary.md"
                with (
                    patch.dict(os.environ, LIVE_CHECKS="true", GITHUB_STEP_SUMMARY=str(summary)),
                    patch.object(validate, "REPO_ROOT", root),
                    patch.object(sys, "argv", ["validate.py", str(fixture)]),
                    patch("_fabric.graph_group_exists") as lookup,
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    if isinstance(outcome, Exception):
                        lookup.side_effect = outcome
                    else:
                        lookup.return_value = outcome
                    self.assertEqual(validate.main(), code)
                for report in (root / "validation-report.md", summary):
                    text = report.read_text()
                    self.assertIn(message, text)
                    self.assertIn("PASS" if code == 0 else "FAIL", text)


if __name__ == "__main__":
    unittest.main()
