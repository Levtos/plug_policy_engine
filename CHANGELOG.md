# Changelog

## 0.1.0

- Extracted Plug Policy Engine from `bennis_toolbox` into the standalone
  `plug_policy_engine` Home Assistant integration.
- Kept `enable_control=false` as the safe default; policy decisions are exposed
  as entities before switch control is enabled.
- Added standalone config flow, services, storage helper, platform wrappers, and
  copied the current pure-engine and flow regression tests.
