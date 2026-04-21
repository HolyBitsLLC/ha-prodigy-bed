"""The Prodigy Bed integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_ENCRYPTION_KEY,
    CONF_EXPECTED_NAME,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
)
from .coordinator import ProdigyBedHub, ProdigyBridgeError

PLATFORMS = [Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Prodigy Bed from a config entry."""
    hub = ProdigyBedHub(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        encryption_key=entry.data[CONF_ENCRYPTION_KEY],
        expected_name=entry.data.get(CONF_EXPECTED_NAME),
    )

    try:
        await hub.async_setup()
    except ProdigyBridgeError as exc:
        await hub.async_disconnect()
        raise ConfigEntryNotReady(str(exc)) from exc

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Prodigy Bed config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hub: ProdigyBedHub = hass.data[DOMAIN].pop(entry.entry_id)
        await hub.async_disconnect()
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
