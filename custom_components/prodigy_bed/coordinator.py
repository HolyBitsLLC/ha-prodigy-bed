"""ESPHome bridge client for Prodigy Bed."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

from aioesphomeapi import APIClient
from aioesphomeapi.model import ButtonInfo, DeviceInfo

from .const import BUTTON_ORDER_INDEX, CLIENT_INFO, REQUIRED_BUTTON_OBJECT_IDS

_LOGGER = logging.getLogger(__name__)


class ProdigyBridgeError(RuntimeError):
    """Raised when the ESPHome bridge is unavailable or invalid."""


@dataclass(frozen=True, slots=True)
class ProdigyBridgeButton:
    """Serializable subset of an ESPHome button entity."""

    object_id: str
    name: str
    key: int


class ProdigyBedHub:
    """Maintain a connection to the ESPHome bridge for a Prodigy bed."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        encryption_key: str,
        expected_name: str | None,
    ) -> None:
        """Initialize the bridge hub."""
        self._client = APIClient(
            host,
            port,
            None,
            noise_psk=encryption_key,
            expected_name=expected_name or None,
            client_info=CLIENT_INFO,
        )
        self._host = host
        self._lock = asyncio.Lock()
        self._connected = False
        self._device_info: DeviceInfo | None = None
        self._buttons: dict[str, ProdigyBridgeButton] = {}

    @property
    def available(self) -> bool:
        """Return whether the last bridge connection attempt succeeded."""
        return self._connected

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return cached ESPHome device info."""
        return self._device_info

    @property
    def title(self) -> str:
        """Return a friendly title for the bridge device."""
        if self._device_info is not None:
            return self._device_info.name
        return self._host

    def iter_buttons(self) -> tuple[ProdigyBridgeButton, ...]:
        """Return supported bridge buttons in stable UI order."""
        return tuple(
            sorted(
                self._buttons.values(),
                key=lambda button: (
                    BUTTON_ORDER_INDEX.get(button.object_id, len(BUTTON_ORDER_INDEX)),
                    button.name,
                ),
            )
        )

    async def async_setup(self) -> None:
        """Connect once and cache bridge metadata."""
        await self.async_refresh_metadata()

    async def async_disconnect(self) -> None:
        """Disconnect the ESPHome API client."""
        async with self._lock:
            try:
                await self._client.disconnect()
            finally:
                self._connected = False

    async def async_refresh_metadata(self) -> None:
        """Refresh bridge device info and supported button metadata."""
        async with self._lock:
            await self._async_ensure_connected_locked()
            await self._async_load_metadata_locked()

    async def async_press_button(self, object_id: str) -> None:
        """Invoke a bridge button by object id."""
        async with self._lock:
            await self._async_ensure_connected_locked()
            button = self._buttons.get(object_id)
            if button is None:
                await self._async_load_metadata_locked()
                button = self._buttons.get(object_id)
            if button is None:
                raise ProdigyBridgeError(f"Unknown Prodigy button: {object_id}")

            try:
                await self._client.button_command(button.key)
            except Exception as exc:
                _LOGGER.warning("Bridge button press failed for %s, reconnecting", object_id)
                self._connected = False
                await self._async_ensure_connected_locked()
                await self._async_load_metadata_locked()
                button = self._buttons.get(object_id)
                if button is None:
                    raise ProdigyBridgeError(f"Unknown Prodigy button after reconnect: {object_id}") from exc
                await self._client.button_command(button.key)

    async def _async_ensure_connected_locked(self) -> None:
        if self._connected:
            return
        try:
            await self._client.connect(log_errors=False)
        except Exception as exc:
            self._connected = False
            raise ProdigyBridgeError(f"Unable to connect to ESPHome bridge at {self._host}") from exc
        self._connected = True

    async def _async_load_metadata_locked(self) -> None:
        try:
            device_info, entities, _services = await self._client.device_info_and_list_entities()
        except Exception as exc:
            self._connected = False
            raise ProdigyBridgeError("Unable to load ESPHome bridge metadata") from exc

        buttons = {
            entity.object_id: ProdigyBridgeButton(
                object_id=entity.object_id,
                name=entity.name,
                key=int(entity.key),
            )
            for entity in entities
            if isinstance(entity, ButtonInfo) and entity.object_id.startswith("bed_")
        }

        missing = REQUIRED_BUTTON_OBJECT_IDS - buttons.keys()
        if missing:
            raise ProdigyBridgeError(
                "ESPHome bridge is missing required Prodigy buttons: "
                + ", ".join(sorted(missing))
            )

        self._device_info = device_info
        self._buttons = buttons
