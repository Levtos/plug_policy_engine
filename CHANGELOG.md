# Changelog

## 0.1.8

- Add a coordinator-local power source fallback for known Einhornzentrale plug
  switches and expose `power_entity` source diagnostics on policy/summary
  sensors.

## 0.1.7

- Prefer direct `hass.states.get(entity_id)` checks when resolving profile
  entities, so coordinator startup/refresh can find Core Devices sensors even
  if `async_entity_ids()` is incomplete during setup.

## 0.1.6

- Resolve missing profile power entities during each coordinator refresh, so
  entries that start before Core Devices sensors are registered still pick up
  `sensor.benni_device_*` power once those states appear.

## 0.1.5

- Add a runtime coordinator fallback for known profile devices whose saved
  config still lacks `power_entity`, so existing entries can read Core Devices
  power immediately after restart even if storage migration did not persist the
  field.

## 0.1.4

- Migrate known Einhornzentrale plug power bindings from missing or old
  raw/atomic plug sensors to their Core Devices sources when available, while
  preserving unrelated custom power sensors.

## 0.1.3

- Bump the ConfigEntry `VERSION` to 3 so Home Assistant actually runs the
  `0.1.2` power-source migration on existing installations.

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
