"""Config flow for Prodigy Bed."""
from __future__ import annotations

from aioesphomeapi import APIClient
from aioesphomeapi.model import ButtonInfo
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CLIENT_INFO,
    CONF_ENCRYPTION_KEY,
    CONF_EXPECTED_NAME,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_PORT,
    DOMAIN,
    REQUIRED_BUTTON_OBJECT_IDS,
)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
        vol.Required(CONF_ENCRYPTION_KEY): str,
        vol.Optional(CONF_EXPECTED_NAME, default=""): str,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate the bridge could not be reached."""


class InvalidProdigyBridge(HomeAssistantError):
    """Error to indicate the ESPHome node is not a Prodigy bridge."""


async def _validate_input(user_input: dict[str, str | int]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    expected_name = str(user_input.get(CONF_EXPECTED_NAME) or "") or None
    client = APIClient(
        str(user_input[CONF_HOST]),
        int(user_input[CONF_PORT]),
        None,
        noise_psk=str(user_input[CONF_ENCRYPTION_KEY]),
        expected_name=expected_name,
        client_info=f"{CLIENT_INFO}-config-flow",
    )

    try:
        await client.connect(log_errors=False)
        device_info, entities, _services = await client.device_info_and_list_entities()
    except Exception as exc:
        raise CannotConnect from exc
    finally:
        await client.disconnect()

    button_ids = {
        entity.object_id
        for entity in entities
        if isinstance(entity, ButtonInfo) and entity.object_id.startswith("bed_")
    }
    missing = REQUIRED_BUTTON_OBJECT_IDS - button_ids
    if missing:
        raise InvalidProdigyBridge(
            "Missing required Prodigy bridge buttons: " + ", ".join(sorted(missing))
        )

    unique_id = getattr(device_info, "mac_address", None) or str(user_input[CONF_HOST])
    return {
        "title": device_info.name,
        "unique_id": str(unique_id).lower(),
    }


class ProdigyBedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Prodigy Bed."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str | int] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await _validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidProdigyBridge:
                errors["base"] = "invalid_bridge"
            else:
                cleaned_input = dict(user_input)
                if not cleaned_input.get(CONF_EXPECTED_NAME):
                    cleaned_input.pop(CONF_EXPECTED_NAME, None)

                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured(updates=cleaned_input)
                return self.async_create_entry(title=info["title"], data=cleaned_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
