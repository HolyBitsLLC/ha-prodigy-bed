"""Basic metadata and constant tests for the Prodigy Bed integration."""
from __future__ import annotations

import json
from pathlib import Path
import tomllib

from custom_components.prodigy_bed.const import (
    BUTTON_ORDER,
    BUTTON_ORDER_INDEX,
    DOMAIN,
    REQUIRED_BUTTON_OBJECT_IDS,
)


def test_manifest_domain_matches_integration_domain() -> None:
    manifest = json.loads(
        Path("custom_components/prodigy_bed/manifest.json").read_text()
    )
    assert manifest["domain"] == DOMAIN


def test_manifest_version_matches_project_version() -> None:
    manifest = json.loads(
        Path("custom_components/prodigy_bed/manifest.json").read_text()
    )
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    assert manifest["version"] == pyproject["project"]["version"]


def test_required_buttons_are_present_in_declared_order() -> None:
    assert REQUIRED_BUTTON_OBJECT_IDS <= set(BUTTON_ORDER)
    assert len(BUTTON_ORDER) == len(set(BUTTON_ORDER))


def test_button_order_index_matches_button_order() -> None:
    for index, object_id in enumerate(BUTTON_ORDER):
        assert BUTTON_ORDER_INDEX[object_id] == index
