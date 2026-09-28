"""Thin Fabric REST client using azure-identity (DefaultAzureCredential).

Auth: in GitHub Actions we use the azure/login@v2 OIDC step to populate
AZURE_CLIENT_ID / AZURE_TENANT_ID / AZURE_FEDERATED_TOKEN_FILE, which
DefaultAzureCredential picks up automatically.
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional
from urllib.parse import urlencode, urlsplit

import requests
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential

FABRIC_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
PBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"

_credential: Optional[DefaultAzureCredential] = None


def _cred() -> DefaultAzureCredential:
    global _credential
    if _credential is None:
        _credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
    return _credential


def token(scope: str = FABRIC_SCOPE) -> str:
    return _cred().get_token(scope).token


def _request(method: str, url: str, *, scope: str = FABRIC_SCOPE,
             json: Any = None, params: dict | None = None,
             expect: tuple[int, ...] = (200, 201, 202, 204),
             retries: int = 5) -> requests.Response:
    headers = {"Authorization": f"Bearer {token(scope)}", "Content-Type": "application/json"}
    if url.startswith(f"{FABRIC_BASE}/"):
        headers["x-ms-fabric-skill"] = "onelake-catalog-govern-cli"
    backoff = 2.0
    for attempt in range(retries):
        r = requests.request(method, url, headers=headers, json=json, params=params, timeout=60)
        if r.status_code in expect:
            return r
        if r.status_code in (429, 502, 503, 504):
            wait = float(r.headers.get("Retry-After", backoff))
            time.sleep(wait)
            backoff *= 2
            continue
        # 401/403 etc — surface immediately
        raise RuntimeError(f"{method} {url} -> {r.status_code}: {r.text}")
    raise RuntimeError(f"{method} {url} exhausted retries; last status {r.status_code}: {r.text}")


# ---------- Workspaces ----------
def _list_pages(base_url: str) -> list[dict]:
    out, url = [], base_url
    seen = set()
    while url:
        if url in seen:
            raise RuntimeError("Repeated Fabric pagination link; inventory is incomplete")
        seen.add(url)
        r = _request("GET", url, expect=(200,))
        body = r.json()
        if not isinstance(body, dict) or not isinstance(body.get("value"), list):
            raise RuntimeError("Invalid Fabric list response; inventory is incomplete")
        if not all(isinstance(item, dict) for item in body["value"]):
            raise RuntimeError("Invalid Fabric list entry; inventory is incomplete")
        out.extend(body["value"])
        if body.get("continuationToken"):
            url = f"{base_url}?{urlencode({'continuationToken': body['continuationToken']})}"
        else:
            url = body.get("continuationUri")
            if url:
                target, base = urlsplit(url), urlsplit(base_url)
                if (target.scheme, target.netloc, target.path) != (
                    base.scheme, base.netloc, base.path
                ):
                    raise RuntimeError("Unexpected Fabric pagination destination")
    return out


def list_workspaces() -> list[dict]:
    return _list_pages(f"{FABRIC_BASE}/workspaces")


def get_workspace_by_name(name: str, workspaces: list[dict] | None = None) -> dict | None:
    workspaces = list_workspaces() if workspaces is None else workspaces
    matches = [w for w in workspaces if (w.get("displayName") or "").casefold() == name.casefold()]
    if len(matches) > 1:
        raise RuntimeError(f"Multiple accessible workspaces match '{name}'; refusing to choose")
    return matches[0] if matches else None


def get_workspace(workspace_id: str) -> dict:
    body = _request("GET", f"{FABRIC_BASE}/workspaces/{workspace_id}", expect=(200,)).json()
    if not isinstance(body, dict) or (body.get("id") or "").casefold() != workspace_id.casefold():
        raise RuntimeError("Workspace readback did not return the requested workspace ID")
    return body


def create_workspace(display_name: str, description: str, capacity_id: str | None = None) -> dict:
    body = {"displayName": display_name, "description": description}
    if capacity_id:
        body["capacityId"] = capacity_id
    r = _request("POST", f"{FABRIC_BASE}/workspaces", json=body, expect=(201, 200))
    return r.json()


def update_workspace(workspace_id: str, *, description: str | None = None) -> None:
    body = {}
    if description is not None:
        body["description"] = description
    if not body:
        return
    _request("PATCH", f"{FABRIC_BASE}/workspaces/{workspace_id}", json=body)


def wait_for_capacity(workspace_id: str, capacity_id: str, *,
                      timeout_seconds: float = 300, poll_seconds: float = 5) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while True:
        workspace = get_workspace(workspace_id)
        status = workspace.get("capacityAssignmentProgress")
        if status == "Failed":
            raise RuntimeError(f"Capacity assignment failed for workspace {workspace_id}")
        if status not in ("Completed", "InProgress"):
            raise RuntimeError(f"Unrecognized capacity assignment status: {status!r}")
        if status == "Completed" and (workspace.get("capacityId") or "").casefold() == capacity_id.casefold():
            return workspace
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"Timed out verifying capacity assignment for workspace {workspace_id}")
        time.sleep(min(poll_seconds, remaining))


def assign_to_capacity(workspace_id: str, capacity_id: str) -> dict:
    _request("POST", f"{FABRIC_BASE}/workspaces/{workspace_id}/assignToCapacity",
             json={"capacityId": capacity_id}, expect=(202,))
    return wait_for_capacity(workspace_id, capacity_id)


def list_role_assignments(workspace_id: str) -> list[dict]:
    return _list_pages(f"{FABRIC_BASE}/workspaces/{workspace_id}/roleAssignments")


def add_role_assignment(workspace_id: str, principal_id: str, principal_type: str, role: str) -> None:
    """principal_type: User | Group | ServicePrincipal ; role: Admin|Member|Contributor|Viewer"""
    body = {"principal": {"id": principal_id, "type": principal_type}, "role": role}
    _request("POST", f"{FABRIC_BASE}/workspaces/{workspace_id}/roleAssignments",
             json=body, expect=(201, 200))


# ---------- Capacities ----------
def list_capacities() -> list[dict]:
    return _list_pages(f"{FABRIC_BASE}/capacities")


def find_capacity_id_by_display_name(display_name: str) -> str | None:
    for c in list_capacities():
        if c.get("displayName") == display_name:
            return c.get("id")
    return None


# ---------- Graph (group existence) ----------
class GraphGroupLookupError(RuntimeError):
    """The group lookup could not be completed reliably."""


def graph_group_exists(object_id: str) -> bool:
    try:
        headers = {"Authorization": f"Bearer {token(GRAPH_SCOPE)}"}
        r = requests.get(f"https://graph.microsoft.com/v1.0/groups/{object_id}",
                         headers=headers, params={"$select": "id"}, timeout=30)
    except AzureError as e:
        raise GraphGroupLookupError("could not authenticate to Microsoft Graph") from e
    except requests.RequestException as e:
        raise GraphGroupLookupError("Microsoft Graph group request failed") from e
    if r.status_code == 404:
        return False
    if r.status_code != 200:
        raise GraphGroupLookupError(
            f"Microsoft Graph group lookup returned HTTP {r.status_code}"
        )
    try:
        body = r.json()
    except ValueError as e:
        raise GraphGroupLookupError("Microsoft Graph returned invalid JSON") from e
    group_id = body.get("id") if isinstance(body, dict) else None
    if not isinstance(group_id, str) or group_id.lower() != object_id.lower():
        raise GraphGroupLookupError("Microsoft Graph did not return the requested group ID")
    return True


def graph_resolve_upn(upn: str) -> str | None:
    headers = {"Authorization": f"Bearer {token(GRAPH_SCOPE)}"}
    r = requests.get(f"https://graph.microsoft.com/v1.0/users/{upn}",
                     headers=headers, timeout=30)
    if r.status_code == 200:
        return r.json().get("id")
    return None
