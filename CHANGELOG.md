# Changelog

## 0.1.2

- Backfill known Benni profile plug devices with existing Core Devices or raw
  power sources when the saved `power_entity` is missing or unavailable.
- Read numeric power from Core Devices sensor attributes (`watt`, `power_w`,
  `power`) so `sensor.benni_device_*` can be used as policy power sources.

## 0.1.1

- Prefill global context selectors from `benni_core_devices`/Core State and
  `benni_media_state`.
- Migrate known legacy YAML and `benni_media_context` global source entity IDs
  to the current Core/Media-State entities.
- Fall back to current Core/Media-State globals when configured global sources
  are missing or unavailable.

## 0.1.0

- Extracted Plug Policy Engine from `bennis_toolbox` into the standalone
  `plug_policy_engine` Home Assistant integration.
- Kept `enable_control=false` as the safe default; policy decisions are exposed
  as entities before switch control is enabled.
- Added standalone config flow, services, storage helper, platform wrappers, and
  copied the current pure-engine and flow regression tests.
