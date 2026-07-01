"""Regression coverage for Core Devices power sources."""
from __future__ import annotations

import sys
import types
from datetime import datetime, timedelta
from pathlib import Path

import tests.plug_policy_engine.test_module_smoke as smoke  # noqa: E402
import pp_engine as engine  # noqa: E402

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
            "sensor.benni_master_pc"
        ):
            return "sensor.benni_master_pc"
        if switch_entity == "switch.kitchen_washing_machine_plug" and hass.states.get(
            "sensor.benni_master_household_plug"
        ):
            return "sensor.benni_master_household_plug"
        return None

    suggest_stub.profile_power_entity = _profile_power_entity
    suggest_stub.base_slug = lambda entity_id: (
        str(entity_id).split(".", 1)[1] if entity_id and "." in str(entity_id) else entity_id
    )
    sys.modules["pp_suggest_stub"] = suggest_stub

    src = (MODULE_DIR / "coordinator.py").read_text(encoding="utf-8")
    src = src.replace("from .const import", "from pp_const import")
    src = src.replace("from . import _suggest", "import pp_suggest_stub as _suggest")
    src = src.replace("from .apply_guard import", "from pp_apply_guard import")
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
        "sensor.benni_master_pc": _FakeState("on", {"watt": 170.0}),
    })
    assert coord._read_power("sensor.benni_master_pc") == 170.0


def test_master_active_attribute_is_separate_from_numeric_watt():
    mod = _load_coordinator_module()
    coord = mod.PlugPolicyCoordinator.__new__(mod.PlugPolicyCoordinator)
    coord.hass = _FakeHass({
        "sensor.benni_master_switch": _FakeState(
            "active",
            {"is_active": True, "watt": 0.0},
        ),
    })

    assert coord._read_power("sensor.benni_master_switch") == 0.0
    assert coord._read_active_hint("sensor.benni_master_switch") == "active"


def test_master_inactive_attribute_is_separate_from_numeric_watt():
    mod = _load_coordinator_module()
    coord = mod.PlugPolicyCoordinator.__new__(mod.PlugPolicyCoordinator)
    coord.hass = _FakeHass({
        "sensor.benni_master_tv": _FakeState(
            "off",
            {"is_active": False, "watt": 39.0},
        ),
    })

    assert coord._read_power("sensor.benni_master_tv") == 39.0
    assert coord._read_active_hint("sensor.benni_master_tv") == "idle"


def test_engine_classifies_semantic_master_power_values():
    cfg = engine.DeviceConfig(
        device_id="switch",
        name="Switch",
        switch_entity="switch.living_switch_plug",
        power_entity="sensor.benni_master_switch",
        active_threshold=50.0,
        idle_threshold=5.0,
    )

    active = engine.evaluate(cfg, engine.DeviceState(switch_state="on", power_w="active"), engine.GlobalContext())
    idle = engine.evaluate(cfg, engine.DeviceState(switch_state="on", power_w="idle"), engine.GlobalContext())

    assert active.active_state == "active"
    assert idle.active_state == "idle"


def test_engine_prefers_active_hint_over_numeric_power():
    cfg = engine.DeviceConfig(
        device_id="tv",
        name="TV",
        switch_entity="switch.tv",
        power_entity="sensor.benni_master_tv",
        active_threshold=8.0,
        idle_threshold=5.0,
    )

    decision = engine.evaluate(
        cfg,
        engine.DeviceState(switch_state="on", power_w=39.0, active_hint="idle"),
        engine.GlobalContext(),
    )

    assert decision.active_state == "idle"
    assert decision.power_w == 39.0


def test_coordinator_backfills_missing_profile_power_entity_at_runtime():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("on"),
        "sensor.benni_master_pc": _FakeState("on", {"watt": 170.0}),
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

    assert coord.configs["living_pc_plug"].power_entity == "sensor.benni_master_pc"
    assert coord._refresh_device_state(coord.configs["living_pc_plug"]).power_w == 170.0


def test_coordinator_reads_master_active_hint_and_keeps_watt_for_display():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("on"),
        "sensor.benni_master_pc": _FakeState("active", {"is_active": True, "watt": 205.0}),
    })
    entry = _FakeEntry({
        "devices": [
            {
                "device_id": "living_pc_plug",
                "name": "PC",
                "switch_entity": "switch.living_pc_plug",
                "power_entity": "sensor.benni_master_pc",
                "policy": "HB",
                "kind": "pc",
            }
        ]
    })

    coord = mod.PlugPolicyCoordinator(hass, entry)
    cfg = coord.configs["living_pc_plug"]
    state = coord._refresh_device_state(cfg)
    decision = engine.evaluate(cfg, state, engine.GlobalContext())

    assert state.power_w == 205.0
    assert state.active_hint == "active"
    assert decision.active_state == "active"
    assert decision.power_w == 205.0


def test_coordinator_marks_pc_switch_on_as_manual_cooldown():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("off"),
        "sensor.benni_master_pc": _FakeState("off", {"is_active": False, "watt": 0.0}),
    })
    entry = _FakeEntry({
        "devices": [
            {
                "device_id": "living_pc_plug",
                "name": "PC",
                "switch_entity": "switch.living_pc_plug",
                "power_entity": "sensor.benni_master_pc",
                "policy": "HB",
                "kind": "pc",
                "manual_on_cooldown_seconds": 900,
                "stable_off_seconds": 0,
            }
        ]
    })

    coord = mod.PlugPolicyCoordinator(hass, entry)
    cfg = coord.configs["living_pc_plug"]
    coord._refresh_device_state(cfg)
    hass.states._states["switch.living_pc_plug"] = _FakeState("on")

    state = coord._refresh_device_state(cfg)
    decision = engine.evaluate(
        cfg,
        state,
        engine.GlobalContext(bio=engine.BIO_SLEEP, now_ts=state.manual_on_until_ts - 100),
    )

    assert state.manual_on_until_ts is not None
    assert decision.desired_switch_state == engine.DESIRED_KEEP
    assert "manual_on_cooldown" in decision.blockers


def test_coordinator_reads_household_master_device_attributes():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.kitchen_washing_machine_plug": _FakeState("on"),
        "sensor.benni_master_household_plug": _FakeState(
            "active",
            {
                "kitchen_washing_machine_plug_active": True,
                "kitchen_washing_machine_plug_watt": 42.0,
                "kitchen_dryer_plug_active": False,
                "kitchen_dryer_plug_watt": 0.0,
                "is_active": False,
            },
        ),
    })
    entry = _FakeEntry({
        "devices": [
            {
                "device_id": "kitchen_washing_machine_plug",
                "name": "Waschmaschine",
                "switch_entity": "switch.kitchen_washing_machine_plug",
                "policy": "AC",
                "kind": "appliance",
            }
        ]
    })

    coord = mod.PlugPolicyCoordinator(hass, entry)
    cfg = coord.configs["kitchen_washing_machine_plug"]
    state = coord._refresh_device_state(cfg)
    decision = engine.evaluate(cfg, state, engine.GlobalContext())

    assert cfg.power_entity == "sensor.benni_master_household_plug"
    assert state.power_w == 42.0
    assert state.active_hint == "active"
    assert decision.active_state == "active"
    assert decision.power_w == 42.0


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

    hass.states._states["sensor.benni_master_pc"] = _FakeState(
        "on",
        {"watt": 170.0},
    )

    assert coord._refresh_device_state(cfg).power_w == 170.0
    assert cfg.power_entity == "sensor.benni_master_pc"


def test_coordinator_replaces_missing_saved_profile_power_entity():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.living_pc_plug": _FakeState("on"),
        "sensor.benni_master_pc": _FakeState("on", {"watt": 170.0}),
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
    assert cfg.power_entity == "sensor.benni_master_pc"


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


@smoke._run
async def test_kitchen_diffuser_command_cooldown_survives_brief_target_state():
    mod = _load_coordinator_module()
    hass = _FakeHass({
        "switch.kitchen_diffuser_plug": _FakeState("off"),
    })
    entry = _FakeEntry({
        "enable_control": False,
        "devices": [
            {
                "device_id": "kitchen_diffuser_plug",
                "name": "Kitchen Diffuser",
                "switch_entity": "switch.kitchen_diffuser_plug",
                "policy": "AO",
                "kind": "diffuser",
            },
        ],
    })
    coord = mod.PlugPolicyCoordinator(hass, entry)
    cfg = coord.configs["kitchen_diffuser_plug"]

    await coord.async_apply_now("kitchen_diffuser_plug")
    hass.states._states["switch.kitchen_diffuser_plug"] = _FakeState("on")
    coord._refresh_device_state(cfg)
    hass.states._states["switch.kitchen_diffuser_plug"] = _FakeState("off")

    await coord.async_apply_now("kitchen_diffuser_plug")

    assert [call["service"] for call in hass.services.calls] == ["turn_on"]


@smoke._run
async def test_repeated_non_latch_reasserts_auto_suspend_device():
    mod = _load_coordinator_module()
    clock = {"ts": 0}
    original_utcnow = mod.dt_util.utcnow
    mod.dt_util.utcnow = lambda: datetime(2026, 6, 14) + timedelta(seconds=clock["ts"])
    try:
        hass = _FakeHass({
            "switch.flaky_plug": _FakeState("off"),
        })
        entry = _FakeEntry({
            "enable_control": False,
            "devices": [
                {
                    "device_id": "flaky_plug",
                    "name": "Flaky Plug",
                    "switch_entity": "switch.flaky_plug",
                    "policy": "AO",
                    "kind": "generic",
                },
            ],
        })
        coord = mod.PlugPolicyCoordinator(hass, entry)

        for ts in (0, 60, 120, 180, 240):
            clock["ts"] = ts
            hass.states._states["switch.flaky_plug"] = _FakeState("off")
            await coord.async_apply_now("flaky_plug")

        assert [call["service"] for call in hass.services.calls] == ["turn_on"] * 5
        assert coord.states["flaky_plug"].suspended is True

        clock["ts"] = 300
        await coord.async_apply_now("flaky_plug")

        assert [call["service"] for call in hass.services.calls] == ["turn_on"] * 5
    finally:
        mod.dt_util.utcnow = original_utcnow
