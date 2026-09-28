"""Shared description provenance for provisioning and drift detection."""
from __future__ import annotations

import re

REPOSITORY_RX = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA_RX = re.compile(r"[0-9a-f]{40}")
MARKER_RX = re.compile(
    r"\n\nmanaged-by:gh:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})\Z"
)


def managed_description(description: str, repository: str, sha: str) -> str:
    if not REPOSITORY_RX.fullmatch(repository) or not SHA_RX.fullmatch(sha):
        raise ValueError("A valid GITHUB_REPOSITORY and full GITHUB_SHA are required")
    if "managed-by:gh:" in description:
        raise ValueError("Manifest descriptions must not contain an automation marker")
    result = f"{description.rstrip()}\n\nmanaged-by:gh:{repository}@{sha}"
    if len(result) > 4000:
        raise ValueError("Description plus management marker exceeds Fabric's 4000-character limit")
    return result


def managed_repository(description: str) -> str | None:
    match = MARKER_RX.search(description)
    return match.group(1) if match else None


def description_matches(actual: str, desired: str, repository: str) -> bool:
    match = MARKER_RX.search(actual)
    if not match or match.group(1).casefold() != repository.casefold():
        return False
    # A deployment records its own commit; unrelated later commits are not drift.
    return actual[:match.start()] == desired.rstrip()
