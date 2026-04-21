"""Coordinator tests for Prodigy Bed."""
from __future__ import annotations

from typing import Any

from aioesphomeapi.model import ButtonInfo, DeviceInfo

from custom_components.prodigy_bed.coordinator import ProdigyBedHub


def _make_button(object_id: str, name: str, key: int) -> ButtonInfo:
    return ButtonInfo(object_id=object_id, name=name, key=key)


class _FakeAPIClient:
    def __init__(self, entities: list[ButtonInfo], *, fail_first_press: bool = False) -> None:
        self._entities = entities
        self._fail_first_press = fail_first_press
        self.button_commands: list[int] = []
        self.connect_calls = 0
        self.device_info = DeviceInfo(name="espbedleft", mac_address="001122334455")

    async def connect(self, log_errors: bool = False) -> None:
        self.connect_calls += 1

    async def disconnect(self) -> None:
        return None

    async def device_info_and_list_entities(self) -> tuple[DeviceInfo, list[ButtonInfo], list[Any]]:
        return self.device_info, list(self._entities), []

    def button_command(self, key: int) -> None:
        if self._fail_first_press:
            self._fail_first_press = False
            raise RuntimeError("temporary button failure")
        self.button_commands.append(key)


async def test_iter_buttons_uses_esphome_normalized_object_ids() -> None:
    """ESPHome-normalized button ids should sort using the declared UI order."""
    hub = ProdigyBedHub(
        host="10.0.19.113",
        port=6053,
        encryption_key="test-noise-key",
        expected_name="espbedleft",
    )
    hub._client = _FakeAPIClient(
        [
            _make_button("bed_under_bed_lights_toggle", "Bed Under-Bed Lights Toggle", 5),
            _make_button("bed_preset_zero_g", "Bed Preset Zero-G", 4),
            _make_button("bed_preset_flat", "Bed Preset Flat", 2),
            _make_button("bed_preset_anti_snore", "Bed Preset Anti-Snore", 3),
            _make_button("bed_bluetooth_connect", "Bed Bluetooth Connect", 1),
        ]
    )

    await hub.async_setup()

    assert [button.object_id for button in hub.iter_buttons()] == [
        "bed_bluetooth_connect",
        "bed_preset_flat",
        "bed_preset_zero_g",
        "bed_preset_anti_snore",
        "bed_under_bed_lights_toggle",
    ]


async def test_async_press_button_retries_once_after_failure() -> None:
    """The hub should reconnect and retry a failed button press once."""
    hub = ProdigyBedHub(
        host="10.0.19.113",
        port=6053,
        encryption_key="test-noise-key",
        expected_name="espbedleft",
    )
    fake_client = _FakeAPIClient(
        [
            _make_button("bed_bluetooth_connect", "Bed Bluetooth Connect", 1),
            _make_button("bed_preset_flat", "Bed Preset Flat", 2),
        ],
        fail_first_press=True,
    )
    hub._client = fake_client

    await hub.async_setup()
    await hub.async_press_button("bed_preset_flat")

    assert fake_client.button_commands == [2]
    assert fake_client.connect_calls == 2