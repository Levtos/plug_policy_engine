"""Tests für die additive Tablet-Display-Policy (v0.2.0, FLEET-156) — HA-frei."""
from __future__ import annotations

import pp_const as C
import pp_engine as E

DISPLAY = "switch.tablet_screen"


def _cfg(**overrides):
    base = dict(
        device_id="tablet1",
        name="Tablet",
        switch_entity="switch.tablet_charger",
        policy=C.POLICY_CS,
        kind=C.KIND_TABLET,
        battery_entity="sensor.tablet_battery",
    )
    base.update(overrides)
    return E.DeviceConfig(**base)


def _state(**overrides):
    s = E.DeviceState()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


def _ctx(**kw):
    return E.GlobalContext(**kw)


def _eval(cfg=None, state=None, ctx=None):
    return E.evaluate(cfg or _cfg(), state or _state(battery_pct=55), ctx or _ctx())


# ----- Display-Regeln -----
def test_display_on_when_home_and_awake():
    d = _eval(
        _cfg(display_entity=DISPLAY),
        _state(battery_pct=55, display_state="off"),
        _ctx(presence=C.PRESENCE_HOME, bio=C.BIO_AWAKE),
    )
    assert d.desired_display_state == C.DESIRED_ON


def test_display_off_when_asleep():
    d = _eval(
        _cfg(display_entity=DISPLAY),
        _state(battery_pct=55, display_state="on"),
        _ctx(presence=C.PRESENCE_HOME, bio=C.BIO_SLEEP),
    )
    assert d.desired_display_state == C.DESIRED_OFF


def test_display_off_when_truly_away():
    d = _eval(
        _cfg(display_entity=DISPLAY),
        _state(battery_pct=55),
        _ctx(presence=C.PRESENCE_AWAY, bio=C.BIO_AWAKE),
    )
    assert d.desired_display_state == C.DESIRED_OFF


def test_display_on_when_bei_eltern_and_awake():
    # bei_eltern zählt als zuhause-artig → kein Lock.
    d = _eval(
        _cfg(display_entity=DISPLAY),
        _state(battery_pct=55),
        _ctx(presence=C.PRESENCE_AT_PARENTS, bio=C.BIO_AWAKE),
    )
    assert d.desired_display_state == C.DESIRED_ON


def test_display_keep_when_presence_unknown():
    d = _eval(
        _cfg(display_entity=DISPLAY),
        _state(battery_pct=55),
        _ctx(presence=None, bio=C.BIO_AWAKE),
    )
    assert d.desired_display_state == C.DESIRED_KEEP


def test_display_keep_when_no_display_entity():
    d = _eval(
        _cfg(display_entity=None),
        _state(battery_pct=55),
        _ctx(presence=C.PRESENCE_HOME, bio=C.BIO_AWAKE),
    )
    assert d.desired_display_state == C.DESIRED_KEEP


# ----- Lade-Policy bleibt unberührt -----
def test_charging_logic_unaffected_low_battery_charges():
    d = _eval(
        _cfg(display_entity=DISPLAY, tablet_low=40, tablet_high=80),
        _state(battery_pct=30, switch_state="off"),
        _ctx(presence=C.PRESENCE_AWAY, bio=C.BIO_SLEEP),
    )
    assert d.desired_switch_state == C.DESIRED_ON      # Laden trotz away/sleep
    assert d.desired_display_state == C.DESIRED_OFF    # Display aber aus


def test_charging_stop_high_battery():
    d = _eval(
        _cfg(display_entity=DISPLAY, tablet_low=40, tablet_high=80),
        _state(battery_pct=85, switch_state="on"),
        _ctx(presence=C.PRESENCE_HOME, bio=C.BIO_AWAKE),
    )
    assert d.desired_switch_state == C.DESIRED_OFF     # Ladeschluss
    assert d.desired_display_state == C.DESIRED_ON     # Display an (home+awake)


# ----- Default für Nicht-Tablet -----
def test_non_tablet_display_defaults_keep():
    d = E.evaluate(
        E.DeviceConfig(device_id="x", name="x", switch_entity="switch.x", kind=C.KIND_GENERIC),
        _state(switch_state="on"),
        _ctx(presence=C.PRESENCE_HOME, bio=C.BIO_AWAKE),
    )
    assert d.desired_display_state == C.DESIRED_KEEP
