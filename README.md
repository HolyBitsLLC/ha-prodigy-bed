# ha-prodigy-bed

Home Assistant custom integration for Leggett & Platt Prodigy beds that are
bridged through the HolyBits ESPHome controller firmware.

This integration talks to the ESPHome API exposed by the ATOM Lite bridge
instead of speaking Bluetooth directly from Home Assistant. That keeps the bed
transport in one place and lets the integration work with the same WiFi +
Bluetooth Classic proxy node already running the firmware.

## Current scope

- Connect to a Prodigy ESPHome bridge over the encrypted ESPHome API
- Expose the bridge's Prodigy button surface as native Home Assistant buttons
- Support manual Bluetooth connect and disconnect for the bed link
- Support preset recall for Flat, Zero-G, Anti-Snore, and Memory 1-4
- Support saving the current bed position to Memory 1-4

## Important protocol note

The Prodigy/Okin transport currently exposes four programmable memory slots
plus named built-in presets. There is no verified fifth programmable memory
slot on this transport, so this integration models four saveable memories and a
larger recall surface.

## Planned follow-up

- Mirror selected sensors and connectivity state from the bridge
- Add curated entities for massage controls
- Add richer device metadata and diagnostics
