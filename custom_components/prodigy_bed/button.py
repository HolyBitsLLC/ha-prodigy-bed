"""Button platform for Prodigy Bed."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BUTTON_ENTITY_CATEGORIES, BUTTON_ICONS, DOMAIN
from .coordinator import ProdigyBedHub, ProdigyBridgeButton


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prodigy Bed button entities."""
    hub: ProdigyBedHub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ProdigyBedButton(entry, hub, button) for button in hub.iter_buttons())


class ProdigyBedButton(ButtonEntity):
    """Represent a button exposed by the ESPHome bridge."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        hub: ProdigyBedHub,
        button: ProdigyBridgeButton,
    ) -> None:
        """Initialize the button entity."""
        self._entry = entry
        self._hub = hub
        self._button = button

        self._attr_unique_id = f"{entry.entry_id}-{button.object_id}"
        self._attr_name = button.name.removeprefix("Bed ")
        self._attr_icon = BUTTON_ICONS.get(button.object_id)
        self._attr_entity_category = BUTTON_ENTITY_CATEGORIES.get(button.object_id)

    @property
    def available(self) -> bool:
        """Return whether the bridge is currently available."""
        return self._hub.available

    @property
    def device_info(self) -> DeviceInfo:
        """Return device metadata for the bridge-backed bed."""
        bridge_info = self._hub.device_info
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._hub.title,
            manufacturer=getattr(bridge_info, "manufacturer", None) or "HolyBits",
            model=getattr(bridge_info, "model", None) or "Prodigy Bed ESPHome Bridge",
            sw_version=getattr(bridge_info, "esphome_version", None),
        )

    async def async_press(self) -> None:
        """Press the underlying bridge button."""
        await self._hub.async_press_button(self._button.object_id)
