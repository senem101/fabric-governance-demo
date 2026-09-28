#!/usr/bin/env python3
"""Validate all manifests, then reconcile only workspaces managed by this repo."""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import requests
import yaml
from azure.core.exceptions import AzureError

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fabric as fab  # noqa: E402
from rules_engine import validate_manifest  # noqa: E402
from workspace_metadata import managed_description, managed_repository  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACES_DIR = REPO_ROOT / "workspaces"
POLICY_PATH = REPO_ROOT / "rules" / "policy.yaml"

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


@dataclass
class WorkspacePlan:
    name: str
    description: str
    capacity_id: str
    owners: list[dict]
    existing: dict | None = None


def log(msg: str) -> None:
    print(msg, flush=True)


def resolve_capacity_id(logical_name: str, policy: dict) -> str:
    cfg = policy.get("approvedCapacities", {}).get(logical_name)
    if not cfg:
        raise RuntimeError(f"capacity '{logical_name}' not in approvedCapacities")
    cap_id = cfg.get("capacityId")
    if cap_id and cap_id != "FILL-ME-AT-FIRST-RUN":
        return cap_id
    fallback = os.environ.get("FABRIC_CAPACITY_ID")
    if fallback:
        return fallback
    if DRY_RUN:
        return "<unresolved-dry-run>"
    looked = fab.find_capacity_id_by_display_name(logical_name.split("-", 1)[0]) or \
             fab.find_capacity_id_by_display_name(logical_name)
    if looked:
        return looked
    raise RuntimeError(
        f"could not resolve capacity id for '{logical_name}'. "
        "Set capacityId in rules/policy.yaml or set FABRIC_CAPACITY_ID env var."
    )


def prepare_workspace(manifest: dict, policy: dict) -> WorkspacePlan:
    result = validate_manifest(manifest, policy)
    for finding in result.findings:
        log(f"  {finding.severity}: {finding.rule_id}: {finding.message}")
    if not result.passed:
        raise ValueError("Manifest validation failed; no Fabric writes performed")

    repository = os.environ.get("GITHUB_REPOSITORY", "")
    sha = os.environ.get("GITHUB_SHA", "")
    if DRY_RUN and not repository and not sha:
        desc = manifest["description"]
        log("  [dry-run] marker preview unavailable without GITHUB_REPOSITORY and GITHUB_SHA")
    else:
        desc = managed_description(manifest["description"], repository, sha)
    cap_id = resolve_capacity_id(manifest["capacity"], policy)
    if not DRY_RUN:
        cap_id = str(UUID(cap_id))
    return WorkspacePlan(
        name=manifest["name"], description=desc, capacity_id=cap_id,
        owners=[dict(owner) for owner in manifest["owners"]],
    )


def preflight_live(plans: list[WorkspacePlan]) -> None:
    workspaces = fab.list_workspaces()
    repository = os.environ["GITHUB_REPOSITORY"]
    for plan in plans:
        existing = fab.get_workspace_by_name(plan.name, workspaces)
        if existing is not None:
            existing = fab.get_workspace(existing["id"])
            if existing.get("displayName") != plan.name:
                raise RuntimeError(f"'{plan.name}' differs from the existing workspace's exact name")
            owner_repo = managed_repository(existing.get("description") or "")
            if not owner_repo or owner_repo.casefold() != repository.casefold():
                raise RuntimeError(
                    f"'{plan.name}' exists without this repository's management marker; "
                    "refusing to adopt or overwrite it"
                )
            if existing.get("type") not in (None, "Workspace"):
                raise RuntimeError(f"'{plan.name}' is not a regular workspace")
        plan.existing = existing
        for owner in plan.owners:
            pid = owner["identifier"]
            if owner["principalType"] == "User" and "@" in pid:
                pid = fab.graph_resolve_upn(pid)
                if not pid:
                    raise RuntimeError(f"Could not resolve a User owner for '{plan.name}'")
            owner["identifier"] = str(UUID(pid))


def role_keys(assignments: list[dict]) -> set[tuple[str, str, str]]:
    return {
        (ra["principal"]["id"].casefold(), ra["principal"]["type"], ra["role"])
        for ra in assignments
    }


def verify_roles(workspace_id: str, desired: set[tuple[str, str, str]], *,
                 timeout_seconds: float = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        if desired <= role_keys(fab.list_role_assignments(workspace_id)):
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"Requested roles not confirmed for workspace {workspace_id}")
        time.sleep(min(5, remaining))


def reconcile_workspace(plan: WorkspacePlan) -> None:
    log(f"--- {plan.name} ---")
    if DRY_RUN:
        log(f"  [dry-run] would ensure workspace exists with capacity={plan.capacity_id}")
        log(f"  [dry-run] would set description: {plan.description}")
        for o in plan.owners:
            log(f"  [dry-run] would assign role {o['role']} to {o['principalType']} {o['identifier']}")
        return

    if plan.existing is None:
        log(f"  creating workspace (capacity={plan.capacity_id})")
        ws = fab.create_workspace(plan.name, plan.description, capacity_id=plan.capacity_id)
        ws_id = ws["id"]
        log(f"  created: {ws_id}")
        fab.wait_for_capacity(ws_id, plan.capacity_id)
    else:
        ws_id = plan.existing["id"]
        log(f"  exists: {ws_id} — updating description + capacity")
        if (plan.existing.get("capacityId") or "").casefold() != plan.capacity_id.casefold():
            fab.assign_to_capacity(ws_id, plan.capacity_id)
        else:
            fab.wait_for_capacity(ws_id, plan.capacity_id)
        fab.update_workspace(ws_id, description=plan.description)

    existing_keys = role_keys(fab.list_role_assignments(ws_id))
    desired = set()
    for owner in plan.owners:
        pid, ptype, role = owner["identifier"], owner["principalType"], owner["role"]
        key = (pid.casefold(), ptype, role)
        desired.add(key)
        if key not in existing_keys:
            log(f"  adding: {ptype} {pid} {role}")
            fab.add_role_assignment(ws_id, pid, ptype, role)
            existing_keys.add(key)
        else:
            log(f"  ok: {ptype} {pid} {role}")

    verify_roles(ws_id, desired)
    actual = fab.wait_for_capacity(ws_id, plan.capacity_id)
    if actual.get("displayName") != plan.name or actual.get("description") != plan.description:
        raise RuntimeError(f"Workspace metadata readback does not match '{plan.name}'")
    log(f"  verified: {ws_id} — description, capacity and requested roles")


def main() -> int:
    files = sorted(WORKSPACES_DIR.glob("*.yaml"))
    if not files:
        log("No manifests to provision.")
        return 0
    try:
        policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
        plans = []
        names = set()
        for path in files:
            log(f"Preflight: {path.name}")
            plan = prepare_workspace(yaml.safe_load(path.read_text(encoding="utf-8")), policy)
            if path.stem != plan.name or plan.name.casefold() in names:
                raise ValueError("Manifest filenames must match unique workspace names")
            names.add(plan.name.casefold())
            plans.append(plan)
        if not DRY_RUN:
            preflight_live(plans)
        for plan in plans:
            reconcile_workspace(plan)
    except (OSError, ValueError, RuntimeError, yaml.YAMLError, AzureError, requests.RequestException) as e:
        log(f"ERROR: {e}")
        log("Provisioning stopped. Earlier writes, if any, are not rolled back; inspect before retrying.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
