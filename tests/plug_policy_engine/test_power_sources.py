"""Regression coverage for Core Devices power sources."""
from __future__ import annotations

import sys
import types
from datetime import datetime
from pathlib import Path

import tests.plug_policy_engine.test_module_smoke as smoke  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "custom_components" / "plug_policy_engine"


class _FakeState:
    def __init__(self, state, attributes=None):
        self.state = state
        self.attributes = attributes or {}


class _FakeStates:
    def __init__(self, states):
        self._states = states

    def get(self, entity_id):
        return self._states.get(entity_id)

    def async_entity_ids(self, domain=None):
        if domain is None:
            return list(self._states)
        return [
            entity_id
            for entity_id in self._states
            if entity_id.startswith(f"{domain}.")
        ]


class _FakeHass:
    def __init__(self, states):
        self.states = _FakeStates(states)
        self.services = _FakeServices()


class _FakeServices:
    def __init__(self):
        self.calls = []

    async def async_call(self, domain, service, data, blocking=False, target=None):
        self.calls.append({
            "domain": domain,
            "service": service,
            "data": data,
            "blocking": blocking,
            "target": target,
        })


class _FakeStore:
    async def async_load(self):
        return {}

    async def async_save(self, data):
        self.data = data


class _FakeEntry:
    entry_id = "entry-1"

    def __init__(self, data, options=None):
        self.data = data
        self.options = options or {}


def _load_coordinator_module():
    if "pp_coordinator_real_power_test" in sys.modules:
        return sys.modules["pp_coordinator_real_power_test"]

    sys.modules.setdefault("homeassistant.helpers.event", types.ModuleType("homeassistant.helpers.event"))
    event_mod = sys.modules["homeassistant.helpers.event"]
    event_mod.async_track_state_change_event = lambda *args, **kwargs: (lambda: None)
    event_mod.async_track_time_interval = lambda *args, **kwargs: (lambda: None)

    ha_const = sys.modules.setdefault("homeassistant.const", types.ModuleType("homeassistant.const"))
    ha_const.EVENT_HOMEASSISTANT_STARTED = "homeassistant_started"

    ha_util = sys.modules.setdefault("homeassistant.util", types.ModuleType("homeassistant.util"))
    ha_util.__path__ = []  # type: ignore[attr-defined]
    dt_mod = sys.modules.setdefault("homeassistant.util.dt", types.ModuleType("homeassistant.util.dt"))
    dt_mod.utcnow = lambda: datetime(2026, 6, 14)

    storage_stub = types.ModuleType("pp_storage_stub")
    storage_stub.make_store = lambda *args, **kwargs: _FakeStore()
    sys.modules["pp_storage_stub"] = storage_stub

    suggest_stub = types.ModuleType("pp_suggest_stub")

    def _profile_power_entity(hass, switch_entity):
        if switch_entity == "switch.living_pc_plug" and hass.states.get(
            "sensor.benni_device_living_pc"
        ):
            return "sensor.benni_device_living_pc"
        return None

    suggest_stub.profile_power_entity = _profile_power_entity
    sys.modules["pp_suggest_stub"] = suggest_stub

    src = (MODULE_DIR / "coordinator.py").read_text(encoding="utf-8")
    src = src.replace("from .const import", "from pp_const import")
    src = src.replace("from . import _suggest", "import pp_suggest_stub as _suggest")
    src = src.replace("from .engine import", "from pp_engine import")
    src = src.replace("from .storage import make_store", "from pp_storage_stub import make_store")
    mod = types.ModuleType("pp_coordinator_real_power_test")
    sys.modules[mod.__name__] = mod
    exec(compile(src, str(MODULE_DIR / "coordinator.py"), "exec"), mod.__dict__)
    return mod


def test_read_power_uses_numeric_sensor_state_first():
    mod = _load_coordinator_module()
    coord = mod.PlugPolicyCoordinator.__new__(mod.PlugPolicyCoordinator)
    coord.hass = _FakeHass({
        "sensor.raw_power": _FakeState("170", {"watt": 1}),
    })
    assert coord._read_power("sensor.raw_power") == "170"


def test_read_power_uses_watt_attribute_for_core_device_sensor():
    mod = _load_coordinator_module()
    coord = mod.PlugPolicyCoordinator.__new__(mod.PlugPolicyCoordinator)
    coord.hass = _FakeHass({
        "sensor.benni_device_living_pc": _FakeState("on", {"watt": 170.0}),
    })
    assert coord._read_power("sensor.benni_device_living_pc") == 170.0


def test_coordinator_backfills_missing_profile_power_entity_at_runtime():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("on"),
        "sensor.benni_device_living_pc": _FakeState("on", {"watt": 170.0}),
    })
    entry = _FakeEntry({
        "devices": [
            {
                "device_id": "living_pc_plug",
                "name": "PC",
                "switch_entity": "switch.living_pc_plug",
                "policy": "HB",
                "kind": "pc",
            }
        ]
    })

    coord = mod.PlugPolicyCoordinator(hass, entry)

    assert coord.configs["living_pc_plug"].power_entity == "sensor.benni_device_living_pc"
    assert coord._refresh_device_state(coord.configs["living_pc_plug"]).power_w == 170.0


def test_coordinator_resolves_profile_power_after_core_device_appears():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("on"),
    })
    entry = _FakeEntry({
        "devices": [
            {
                "device_id": "living_pc_plug",
                "name": "PC",
                "switch_entity": "switch.living_pc_plug",
                "policy": "HB",
                "kind": "pc",
            }
        ]
    })
    coord = mod.PlugPolicyCoordinator(hass, entry)
    cfg = coord.configs["living_pc_plug"]
    assert cfg.power_entity is None

    hass.states._states["sensor.benni_device_living_pc"] = _FakeState(
        "on",
        {"watt": 170.0},
    )

    assert coord._refresh_device_state(cfg).power_w == 170.0
    assert cfg.power_entity == "sensor.benni_device_living_pc"


def test_coordinator_replaces_missing_saved_profile_power_entity():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("on"),
        "sensor.benni_device_living_pc": _FakeState("on", {"watt": 170.0}),
    })
    entry = _FakeEntry({
        "devices": [
            {
                "device_id": "living_pc_plug",
                "name": "PC",
                "switch_entity": "switch.living_pc_plug",
                "power_entity": "sensor.living_pc_plug_power_atomic",
                "policy": "HB",
                "kind": "pc",
            }
        ]
    })
    coord = mod.PlugPolicyCoordinator(hass, entry)
    cfg = coord.configs["living_pc_plug"]

    assert coord._refresh_device_state(cfg).power_w == 170.0
    assert cfg.power_entity == "sensor.benni_device_living_pc"


def test_read_power_preserves_unknown_when_no_numeric_power_exists():
    mod = _load_coordinator_module()
    coord = mod.PlugPolicyCoordinator.__new__(mod.PlugPolicyCoordinator)
    coord.hass = _FakeHass({
        "sensor.device_without_power": _FakeState("on", {"watt": None}),
    })
    assert coord._read_power("sensor.device_without_power") == "on"


@smoke._run
async def test_apply_now_with_device_only_calls_selected_switch():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.target_plug": _FakeState("off"),
        "switch.other_plug": _FakeState("off"),
    })
    entry = _FakeEntry({
        "enable_control": False,
        "devices": [
            {
                "device_id": "target_plug",
                "name": "Target",
                "switch_entity": "switch.target_plug",
                "policy": "AO",
                "kind": "generic",
            },
            {
                "device_id": "other_plug",
                "name": "Other",
                "switch_entity": "switch.other_plug",
                "policy": "AO",
                "kind": "generic",
            },
        ],
    })
    coord = mod.PlugPolicyCoordinator(hass, entry)

    await coord.async_apply_now("target_plug")

    assert coord.enable_control is False
    assert [call["target"] for call in hass.services.calls] == [
        {"entity_id": "switch.target_plug"},
    ]
    assert "target_plug" in coord.decisions
    assert "other_plug" not in coord.decisions
