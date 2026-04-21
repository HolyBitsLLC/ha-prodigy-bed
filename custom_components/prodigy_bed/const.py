"""Constants for the Prodigy Bed integration."""
from __future__ import annotations

from homeassistant.const import EntityCategory

DOMAIN = "prodigy_bed"

CONF_ENCRYPTION_KEY = "encryption_key"
CONF_EXPECTED_NAME = "expected_name"
CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_PORT = 6053
CLIENT_INFO = "ha-prodigy-bed"

REQUIRED_BUTTON_OBJECT_IDS = frozenset(
    {
        "bed_bluetooth_connect",
        "bed_preset_flat",
    }
)

BUTTON_ORDER = (
    "bed_bluetooth_connect",
    "bed_bluetooth_disconnect",
    "bed_preset_flat",
    "bed_preset_zero-g",
    "bed_preset_anti-snore",
    "bed_preset_memory_1",
    "bed_preset_memory_2",
    "bed_preset_memory_3",
    "bed_preset_memory_4",
    "bed_save_to_memory_1",
    "bed_save_to_memory_2",
    "bed_save_to_memory_3",
    "bed_save_to_memory_4",
    "bed_head_up",
    "bed_head_down",
    "bed_foot_up",
    "bed_foot_down",
    "bed_stop",
    "bed_under-bed_lights_toggle",
)

BUTTON_ORDER_INDEX = {object_id: index for index, object_id in enumerate(BUTTON_ORDER)}

BUTTON_ENTITY_CATEGORIES = {
    "bed_bluetooth_connect": EntityCategory.CONFIG,
    "bed_bluetooth_disconnect": EntityCategory.CONFIG,
    "bed_save_to_memory_1": EntityCategory.CONFIG,
    "bed_save_to_memory_2": EntityCategory.CONFIG,
    "bed_save_to_memory_3": EntityCategory.CONFIG,
    "bed_save_to_memory_4": EntityCategory.CONFIG,
}

BUTTON_ICONS = {
    "bed_bluetooth_connect": "mdi:bluetooth-connect",
    "bed_bluetooth_disconnect": "mdi:bluetooth-off",
    "bed_preset_flat": "mdi:bed-empty",
    "bed_preset_zero-g": "mdi:rotate-orbit",
    "bed_preset_anti-snore": "mdi:sleep",
    "bed_preset_memory_1": "mdi:numeric-1-box",
    "bed_preset_memory_2": "mdi:numeric-2-box",
    "bed_preset_memory_3": "mdi:numeric-3-box",
    "bed_preset_memory_4": "mdi:numeric-4-box",
    "bed_save_to_memory_1": "mdi:content-save-outline",
    "bed_save_to_memory_2": "mdi:content-save-outline",
    "bed_save_to_memory_3": "mdi:content-save-outline",
    "bed_save_to_memory_4": "mdi:content-save-outline",
    "bed_head_up": "mdi:arrow-up-bold-circle",
    "bed_head_down": "mdi:arrow-down-bold-circle",
    "bed_foot_up": "mdi:arrow-up-bold-circle-outline",
    "bed_foot_down": "mdi:arrow-down-bold-circle-outline",
    "bed_stop": "mdi:stop-circle",
    "bed_under-bed_lights_toggle": "mdi:lightbulb",
}
