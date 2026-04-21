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

## Local k3s smoke test

For a disposable Home Assistant smoke environment on the existing `k3s`
context, apply [k8s/local-k3s/home-assistant-smoke.yaml](k8s/local-k3s/home-assistant-smoke.yaml)
and port-forward the service:

```bash
kubectl --context k3s apply -f k8s/local-k3s/home-assistant-smoke.yaml
kubectl --context k3s -n home-assistant-local rollout status deploy/home-assistant
kubectl --context k3s -n home-assistant-local port-forward svc/home-assistant 8123:8123
```

The manifest installs `custom_components/prodigy_bed` from this repo's `main`
branch into `/config/custom_components` on startup so the local Home Assistant
pod exercises the same integration payload that ships publicly.
