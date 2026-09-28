import contextlib
import copy
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import _fabric
import drift
import provision
import rules_engine
from workspace_metadata import description_matches, managed_description, managed_repository


REPOSITORY = "example/governance"
SHA = "a" * 40
OLD_SHA = "b" * 40
CAPACITY_ID = "11111111-aaaa-bbbb-cccc-555555555555"
WORKSPACE_ID = "22222222-3333-4444-5555-666666666666"
GROUP_ID = "33333333-4444-5555-6666-777777777777"
USER_ID = "44444444-5555-6666-7777-888888888888"
DESCRIPTION = "Training workspace with synthetic data and no customer information."


def response(body, status=200):
    return Mock(status_code=status, headers={}, json=Mock(return_value=body))


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, LIVE_CHECKS="false",
                                     GITHUB_REPOSITORY=REPOSITORY, GITHUB_SHA=SHA))
        self.enterContext(patch("_fabric.token", return_value="test-token"))
        self.enterContext(patch("_fabric.requests.request", side_effect=AssertionError("Unexpected HTTP")))
        self.enterContext(patch("_fabric.requests.get", side_effect=AssertionError("Unexpected Graph")))


class MetadataTests(OfflineTestCase):
    def test_marker_records_repository_and_commit(self):
        actual = managed_description(DESCRIPTION, REPOSITORY, SHA)
        self.assertEqual(actual, f"{DESCRIPTION}\n\nmanaged-by:gh:{REPOSITORY}@{SHA}")
        self.assertEqual(managed_repository(actual), REPOSITORY)

    def test_drift_ignores_only_commit_of_same_repository_marker(self):
        actual = managed_description(DESCRIPTION, REPOSITORY, OLD_SHA)
        self.assertTrue(description_matches(actual, DESCRIPTION, REPOSITORY))
        self.assertFalse(description_matches(actual, DESCRIPTION, "other/repo"))
        self.assertFalse(description_matches(actual, DESCRIPTION, ""))
        self.assertFalse(description_matches(actual, DESCRIPTION + " edited", REPOSITORY))
        self.assertFalse(description_matches(DESCRIPTION, DESCRIPTION, REPOSITORY))
        self.assertFalse(description_matches(actual.replace(OLD_SHA, "invalid"), DESCRIPTION, REPOSITORY))

    def test_invalid_context_reserved_marker_and_length_fail(self):
        for repo, sha in (("", SHA), (REPOSITORY, ""), ("not-a-repo", SHA), (REPOSITORY, "abc")):
            with self.subTest(repo=repo, sha=sha), self.assertRaises(ValueError):
                managed_description(DESCRIPTION, repo, sha)
        with self.assertRaisesRegex(ValueError, "automation marker"):
            managed_description(DESCRIPTION + " managed-by:gh:manual", REPOSITORY, SHA)
        marker_size = len(managed_description("", REPOSITORY, SHA))
        self.assertEqual(len(managed_description("x" * (4000 - marker_size), REPOSITORY, SHA)), 4000)
        with self.assertRaisesRegex(ValueError, "4000"):
            managed_description("x" * (4001 - marker_size), REPOSITORY, SHA)


class FabricClientTests(OfflineTestCase):
    def test_workspace_pagination_supports_encoded_tokens(self):
        with patch("_fabric._request", side_effect=[
            response({"value": [{"id": "first"}], "continuationToken": "a+b/c="}),
            response({"value": [{"id": "second"}]}),
        ]) as request:
            self.assertEqual(_fabric.list_workspaces(), [{"id": "first"}, {"id": "second"}])
        self.assertIn("continuationToken=a%2Bb%2Fc%3D", request.call_args_list[1].args[1])

    def test_role_and_capacity_lists_follow_continuation_uri(self):
        for base, read in (
            (f"{_fabric.FABRIC_BASE}/workspaces/{WORKSPACE_ID}/roleAssignments",
             lambda: _fabric.list_role_assignments(WORKSPACE_ID)),
            (f"{_fabric.FABRIC_BASE}/capacities", _fabric.list_capacities),
        ):
            with self.subTest(base=base), patch("_fabric._request", side_effect=[
                response({"value": [], "continuationUri": base + "?continuationToken=next"}),
                response({"value": [{"id": "last-page"}]}),
            ]):
                self.assertEqual(read(), [{"id": "last-page"}])

    def test_invalid_or_repeated_pagination_fails_closed(self):
        bodies = [
            {}, {"value": None}, {"value": ["invalid"]},
            {"value": [], "continuationUri": "https://other.example/v1/workspaces"},
            {"value": [], "continuationUri": f"{_fabric.FABRIC_BASE}/capacities"},
            {"value": [], "continuationToken": "repeated"},
        ]
        for body in bodies:
            with self.subTest(body=body), patch("_fabric._request", return_value=response(body)):
                with self.assertRaises(RuntimeError):
                    _fabric.list_workspaces()

    def test_duplicate_names_are_ambiguous(self):
        with self.assertRaisesRegex(RuntimeError, "Multiple"):
            _fabric.get_workspace_by_name("demo", [{"displayName": "demo"}, {"displayName": "DEMO"}])
        self.assertIsNone(_fabric.get_workspace_by_name("demo", []))

    def test_workspace_readback_must_match_requested_id(self):
        for body in ({}, [], {"id": USER_ID}):
            with self.subTest(body=body), patch("_fabric._request", return_value=response(body)):
                with self.assertRaises(RuntimeError):
                    _fabric.get_workspace(WORKSPACE_ID)

    def test_capacity_202_waits_for_completed_target_assignment(self):
        pending = {"capacityAssignmentProgress": "InProgress", "capacityId": CAPACITY_ID}
        completed = {"capacityAssignmentProgress": "Completed", "capacityId": CAPACITY_ID.upper()}
        with (
            patch("_fabric._request", return_value=response({}, 202)) as request,
            patch("_fabric.get_workspace", side_effect=[pending, completed]) as get,
            patch("_fabric.time.sleep") as sleep,
        ):
            self.assertEqual(_fabric.assign_to_capacity(WORKSPACE_ID, CAPACITY_ID), completed)
        self.assertEqual(get.call_count, 2)
        sleep.assert_called_once()
        self.assertEqual(request.call_args.kwargs["expect"], (202,))

    def test_capacity_failure_or_unknown_status_is_not_success(self):
        for status in ("Failed", None, "NewStatus"):
            with self.subTest(status=status), patch("_fabric.get_workspace", return_value={
                "capacityAssignmentProgress": status, "capacityId": CAPACITY_ID,
            }):
                with self.assertRaises(RuntimeError):
                    _fabric.wait_for_capacity(WORKSPACE_ID, CAPACITY_ID)

    def test_capacity_timeout_for_in_progress_or_wrong_capacity(self):
        for status, capacity in (("InProgress", CAPACITY_ID), ("Completed", USER_ID)):
            with (
                self.subTest(status=status),
                patch("_fabric.get_workspace", return_value={
                    "capacityAssignmentProgress": status, "capacityId": capacity,
                }),
                patch("_fabric.time.monotonic", side_effect=[0, 10]),
            ):
                with self.assertRaisesRegex(RuntimeError, "Timed out"):
                    _fabric.wait_for_capacity(WORKSPACE_ID, CAPACITY_ID, timeout_seconds=5)

    def test_fabric_attribution_header_is_present(self):
        with patch("_fabric.requests.request", return_value=response({})) as request:
            _fabric._request("GET", f"{_fabric.FABRIC_BASE}/workspaces")
        self.assertEqual(request.call_args.kwargs["headers"]["x-ms-fabric-skill"],
                         "onelake-catalog-govern-cli")


class ProvisioningTests(OfflineTestCase):
    def setUp(self):
        super().setUp()
        self.output = self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.enterContext(patch.object(provision, "DRY_RUN", False))
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        workspaces = root / "workspaces"
        workspaces.mkdir()
        self.enterContext(patch.object(provision, "WORKSPACES_DIR", workspaces))
        self.enterContext(patch.object(provision, "POLICY_PATH", root / "policy.yaml"))
        self.manifest = rules_engine.load_yaml(
            rules_engine.REPO_ROOT / "workspaces" / "tr-nlyt-sample-ndf-dev-hello1.yaml"
        )
        self.manifest["description"] = DESCRIPTION
        self.manifest["owners"] = [
            {"principalType": "Group", "identifier": GROUP_ID, "role": "Admin"},
            {"principalType": "User", "identifier": USER_ID, "role": "Member"},
        ]
        self.policy = rules_engine.load_policy()
        self.policy["approvedCapacities"][self.manifest["capacity"]]["capacityId"] = CAPACITY_ID
        provision.POLICY_PATH.write_text(yaml.safe_dump(self.policy), encoding="utf-8")
        self.write_manifest(self.manifest)
        self.actual = {
            "id": WORKSPACE_ID, "displayName": self.manifest["name"], "type": "Workspace",
            "description": managed_description(DESCRIPTION, REPOSITORY, SHA),
            "capacityId": CAPACITY_ID, "capacityAssignmentProgress": "Completed",
        }
        self.roles = [
            {"principal": {"id": GROUP_ID, "type": "Group"}, "role": "Admin"},
            {"principal": {"id": USER_ID, "type": "User"}, "role": "Member"},
        ]
        self.list_ws = self.enterContext(patch("_fabric.list_workspaces", return_value=[]))
        self.get_ws = self.enterContext(patch("_fabric.get_workspace", return_value=self.actual))
        self.create = self.enterContext(patch("_fabric.create_workspace", return_value=self.actual))
        self.update = self.enterContext(patch("_fabric.update_workspace"))
        self.assign = self.enterContext(patch("_fabric.assign_to_capacity", return_value=self.actual))
        self.wait = self.enterContext(patch("_fabric.wait_for_capacity", return_value=self.actual))
        self.list_roles = self.enterContext(patch("_fabric.list_role_assignments", return_value=self.roles))
        self.add = self.enterContext(patch("_fabric.add_role_assignment"))
        self.resolve_user = self.enterContext(patch("_fabric.graph_resolve_upn"))

    def write_manifest(self, manifest):
        (provision.WORKSPACES_DIR / f"{manifest['name']}.yaml").write_text(
            yaml.safe_dump(manifest), encoding="utf-8"
        )

    def assert_no_writes(self):
        self.create.assert_not_called()
        self.update.assert_not_called()
        self.assign.assert_not_called()
        self.add.assert_not_called()

    def test_create_applies_marker_and_verifies_capacity_and_roles(self):
        self.list_roles.side_effect = [[], self.roles]
        self.assertEqual(provision.main(), 0)
        self.create.assert_called_once_with(
            self.manifest["name"], self.actual["description"], capacity_id=CAPACITY_ID
        )
        self.assertEqual(self.add.call_count, 2)
        self.assertEqual(self.wait.call_count, 2)
        self.resolve_user.assert_not_called()
        self.assertIn("verified:", self.output.getvalue())

    def test_repeated_run_preserves_extra_roles_and_does_not_recreate(self):
        self.list_ws.return_value = [self.actual]
        self.get_ws.return_value = dict(self.actual, description=managed_description(DESCRIPTION, REPOSITORY, OLD_SHA))
        self.list_roles.return_value = self.roles + [
            {"principal": {"id": CAPACITY_ID, "type": "ServicePrincipal"}, "role": "Admin"}
        ]
        self.assertEqual(provision.main(), 0)
        self.create.assert_not_called()
        self.assign.assert_not_called()
        self.add.assert_not_called()
        self.update.assert_called_once_with(WORKSPACE_ID, description=self.actual["description"])

    def test_dry_run_never_reads_or_writes_fabric(self):
        with patch.object(provision, "DRY_RUN", True):
            self.assertEqual(provision.main(), 0)
        self.assert_no_writes()
        self.list_ws.assert_not_called()
        self.get_ws.assert_not_called()
        self.resolve_user.assert_not_called()
        self.assertIn(f"managed-by:gh:{REPOSITORY}@{SHA}", self.output.getvalue())

    def test_local_dry_run_explicitly_reports_missing_marker_context(self):
        with patch.object(provision, "DRY_RUN", True), patch.dict(os.environ, GITHUB_REPOSITORY="", GITHUB_SHA=""):
            self.assertEqual(provision.main(), 0)
        self.assertIn("marker preview unavailable", self.output.getvalue())
        self.assert_no_writes()

    def test_invalid_second_manifest_blocks_entire_batch_before_writes(self):
        invalid = copy.deepcopy(self.manifest)
        invalid.update(name="tr-nlyt-sales-ndf-dev-lab01", subject="sales", suffix="lab01", costCenter="CC-0000")
        self.write_manifest(invalid)
        self.assertEqual(provision.main(), 1)
        self.list_ws.assert_not_called()
        self.assert_no_writes()

    def test_invalid_context_and_marker_length_fail_before_fabric(self):
        with patch.dict(os.environ, GITHUB_SHA=""):
            self.assertEqual(provision.main(), 1)
        self.manifest["description"] = "x" * 4000
        self.write_manifest(self.manifest)
        self.assertEqual(provision.main(), 1)
        self.list_ws.assert_not_called()
        self.assert_no_writes()

    def test_filename_must_match_manifest_name(self):
        path = next(provision.WORKSPACES_DIR.glob("*.yaml"))
        path.rename(path.with_name("wrong-name.yaml"))
        self.assertEqual(provision.main(), 1)
        self.assert_no_writes()

    def test_unmanaged_foreign_or_duplicate_workspace_is_not_adopted(self):
        for description in (DESCRIPTION, managed_description(DESCRIPTION, "other/repo", SHA)):
            with self.subTest(description=description):
                self.list_ws.return_value = [self.actual]
                self.get_ws.return_value = dict(self.actual, description=description)
                self.assertEqual(provision.main(), 1)
                self.assert_no_writes()
        self.list_ws.return_value = [self.actual, self.actual]
        self.assertEqual(provision.main(), 1)
        self.assert_no_writes()

    def test_unresolved_user_or_non_guid_owner_fails_before_creation(self):
        for identifier in ("demo@example.com", "not-a-guid"):
            with self.subTest(identifier=identifier):
                self.manifest["owners"][1]["identifier"] = identifier
                self.write_manifest(self.manifest)
                self.resolve_user.return_value = None
                self.assertEqual(provision.main(), 1)
                self.assert_no_writes()

    def test_case_variant_name_is_not_silently_updated(self):
        self.list_ws.return_value = [dict(self.actual, displayName=self.manifest["name"].upper())]
        self.get_ws.return_value = self.list_ws.return_value[0]
        self.assertEqual(provision.main(), 1)
        self.assert_no_writes()

    def test_later_owner_failure_prevents_first_workspace_creation(self):
        invalid = copy.deepcopy(self.manifest)
        invalid.update(name="tr-nlyt-sample-ndf-dev-zlast", suffix="zlast")
        invalid["owners"][1]["identifier"] = "not-a-guid"
        self.write_manifest(invalid)
        self.assertEqual(provision.main(), 1)
        self.assert_no_writes()

    def test_capacity_failure_stops_before_role_changes(self):
        self.wait.side_effect = RuntimeError("Capacity assignment failed")
        self.assertEqual(provision.main(), 1)
        self.add.assert_not_called()
        self.assertNotIn("verified:", self.output.getvalue())

    def test_reassignment_failure_is_not_only_a_warning(self):
        self.list_ws.return_value = [self.actual]
        self.get_ws.return_value = dict(self.actual, capacityId=USER_ID)
        self.assign.side_effect = RuntimeError("HTTP 403")
        self.assertEqual(provision.main(), 1)
        self.update.assert_not_called()
        self.add.assert_not_called()

    def test_role_write_failure_returns_nonzero(self):
        self.list_roles.return_value = []
        self.add.side_effect = RuntimeError("HTTP 403")
        self.assertEqual(provision.main(), 1)
        self.assertIn("Earlier writes", self.output.getvalue())
        self.assertNotIn("verified:", self.output.getvalue())

    def test_metadata_readback_mismatch_returns_nonzero(self):
        self.wait.return_value = dict(self.actual, description="unexpected description")
        self.assertEqual(provision.main(), 1)
        self.assertNotIn("verified:", self.output.getvalue())

    def test_role_readback_retries_and_times_out_explicitly(self):
        desired = provision.role_keys(self.roles)
        self.list_roles.side_effect = [[], self.roles]
        with patch("provision.time.sleep") as sleep:
            provision.verify_roles(WORKSPACE_ID, desired)
        sleep.assert_called_once()
        self.list_roles.side_effect = None
        self.list_roles.return_value = []
        with patch("provision.time.monotonic", side_effect=[0, 10]):
            with self.assertRaisesRegex(RuntimeError, "not confirmed"):
                provision.verify_roles(WORKSPACE_ID, desired, timeout_seconds=5)

    def test_drift_uses_detail_and_ignores_old_commit_but_not_changed_body(self):
        with (
            patch.object(drift, "WORKSPACES_DIR", provision.WORKSPACES_DIR),
            patch.object(drift, "REPO_ROOT", provision.WORKSPACES_DIR.parent),
            patch.dict(os.environ, GITHUB_STEP_SUMMARY=""),
        ):
            self.list_ws.return_value = [dict(self.actual, description="list summary is not authoritative")]
            self.get_ws.return_value = dict(self.actual, description=managed_description(DESCRIPTION, REPOSITORY, OLD_SHA))
            self.assertEqual(drift.main(), 0)
            self.get_ws.return_value = dict(self.actual, description=managed_description(DESCRIPTION + " changed", REPOSITORY, OLD_SHA))
            self.assertEqual(drift.main(), 2)
            self.get_ws.return_value = dict(self.actual, description=DESCRIPTION)
            self.assertEqual(drift.main(), 2)


if __name__ == "__main__":
    unittest.main()
