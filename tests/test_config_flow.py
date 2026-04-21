"""Config flow tests for Prodigy Bed."""
from __future__ import annotations

from typing import Any

from aioesphomeapi.model import ButtonInfo, DeviceInfo
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.prodigy_bed.const import (
    CONF_ENCRYPTION_KEY,
    CONF_EXPECTED_NAME,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_PORT,
    DOMAIN,
)


def _make_button(object_id: str, name: str, key: int) -> ButtonInfo:
    return ButtonInfo(object_id=object_id, name=name, key=key)


class _FakeAPIClient:
    entities: list[ButtonInfo] = []
    device_info = DeviceInfo(name="espbedleft", mac_address="001122334455")

    def __init__(self, host: str, port: int, password: str | None, **kwargs: Any) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.kwargs = kwargs

    async def connect(self, log_errors: bool = False) -> None:
        return None

    async def disconnect(self) -> None:
        return None

    async def device_info_and_list_entities(self) -> tuple[DeviceInfo, list[ButtonInfo], list[Any]]:
        return self.device_info, list(self.entities), []


async def test_user_flow_creates_entry(hass, monkeypatch) -> None:
    """A valid bridge should create a config entry."""

    class FakeAPIClient(_FakeAPIClient):
        entities = [
            _make_button("bed_bluetooth_connect", "Bed Bluetooth Connect", 1),
            _make_button("bed_preset_flat", "Bed Preset Flat", 2),
            _make_button("bed_preset_zero_g", "Bed Preset Zero-G", 3),
        ]

    monkeypatch.setattr("custom_components.prodigy_bed.config_flow.APIClient", FakeAPIClient)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data={
            CONF_HOST: "10.0.19.113",
            CONF_PORT: DEFAULT_PORT,
            CONF_ENCRYPTION_KEY: "test-noise-key",
            CONF_EXPECTED_NAME: "",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "espbedleft"
    assert result["data"] == {
        CONF_HOST: "10.0.19.113",
        CONF_PORT: DEFAULT_PORT,
        CONF_ENCRYPTION_KEY: "test-noise-key",
    }


async def test_user_flow_rejects_non_bridge(hass, monkeypatch) -> None:
    """A node missing required buttons should be rejected."""

    class FakeAPIClient(_FakeAPIClient):
        entities = [_make_button("bed_head_up", "Bed Head Up", 1)]

    monkeypatch.setattr("custom_components.prodigy_bed.config_flow.APIClient", FakeAPIClient)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data={
            CONF_HOST: "10.0.19.113",
            CONF_PORT: DEFAULT_PORT,
            CONF_ENCRYPTION_KEY: "test-noise-key",
            CONF_EXPECTED_NAME: "espbedleft",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_bridge"}