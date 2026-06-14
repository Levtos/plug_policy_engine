"""Regression coverage for Core Devices power sources."""
from __future__ import annotations

import sys
import types
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


class _FakeHass:
    def __init__(self, states):
        self.states = _FakeStates(states)


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
    dt_mod.utcnow = lambda: __import__("datetime").datetime.datetime(2026, 6, 14)

    storage_stub = types.ModuleType("pp_storage_stub")
    storage_stub.make_store = lambda *args, **kwargs: None
    sys.modules["pp_storage_stub"] = storage_stub

    src = (MODULE_DIR / "coordinator.py").read_text(encoding="utf-8")
    src = src.replace("from .const import", "from pp_const import")
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


def test_read_power_preserves_unknown_when_no_numeric_power_exists():
    mod = _load_coordinator_module()
    coord = mod.PlugPolicyCoordinator.__new__(mod.PlugPolicyCoordinator)
    coord.hass = _FakeHass({
        "sensor.device_without_power": _FakeState("on", {"watt": None}),
    })
    assert coord._read_power("sensor.device_without_power") == "on"

