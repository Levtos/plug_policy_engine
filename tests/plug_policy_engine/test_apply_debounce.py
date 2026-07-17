"""Unit tests for the apply-layer command de-bounce — HA-free (FLEET-107)."""

from __future__ import annotations

import pp_apply_guard as G


def test_no_last_command_allows():
    assert G.debounce_suppresses(None, "turn_on", now_ts=100.0, interval=30.0) is False


def test_same_command_within_window_suppressed():
    # plug dropped its state and we want to re-assert the same command too soon
    last = ("turn_on", 100.0)
    assert G.debounce_suppresses(last, "turn_on", now_ts=110.0, interval=30.0) is True


def test_same_command_after_window_allowed():
    last = ("turn_on", 100.0)
    assert G.debounce_suppresses(last, "turn_on", now_ts=131.0, interval=30.0) is False


def test_direction_change_always_allowed():
    # a genuine opposite command (e.g. stop on sleep) must never be delayed
    last = ("turn_on", 100.0)
    assert G.debounce_suppresses(last, "turn_off", now_ts=101.0, interval=30.0) is False


def test_zero_interval_disables_debounce():
    last = ("turn_on", 100.0)
    assert G.debounce_suppresses(last, "turn_on", now_ts=100.5, interval=0.0) is False


def test_exact_boundary_not_suppressed():
    last = ("turn_on", 100.0)
    # elapsed == interval is no longer "within" the window
    assert G.debounce_suppresses(last, "turn_on", now_ts=130.0, interval=30.0) is False


def test_default_interval_is_thirty_seconds():
    assert G.MIN_COMMAND_INTERVAL_SECONDS == 30.0
    last = ("turn_on", 0.0)
    # uses the module default when interval is omitted
    assert G.debounce_suppresses(last, "turn_on", now_ts=10.0) is True


def test_reassert_history_suspends_on_threshold():
    history = []
    should_suspend = False
    for now_ts in (0.0, 60.0, 120.0, 180.0, 240.0):
        history, should_suspend = G.record_reassert_and_should_suspend(
            history,
            "turn_on",
            now_ts,
            threshold=5,
            window=600.0,
        )
    assert len(history) == 5
    assert should_suspend is True


def test_reassert_history_ignores_opposite_direction():
    history = [("turn_off", 0.0), ("turn_on", 60.0)]
    history, should_suspend = G.record_reassert_and_should_suspend(
        history,
        "turn_on",
        120.0,
        threshold=3,
        window=600.0,
    )
    assert history == [("turn_on", 60.0), ("turn_on", 120.0)]
    assert should_suspend is False


def test_reassert_history_prunes_old_attempts():
    history = [("turn_on", 0.0), ("turn_on", 60.0)]
    history, should_suspend = G.record_reassert_and_should_suspend(
        history,
        "turn_on",
        700.0,
        threshold=3,
        window=600.0,
    )
    assert history == [("turn_on", 700.0)]
    assert should_suspend is False


def test_unavailable_display_target_blocks_service_call():
    assert G.service_target_state_available("unavailable") is False
    assert G.service_target_state_available("unknown") is False
    assert G.service_target_state_available(None) is False
    assert G.service_target_state_available("off") is True


def test_tablet_unknown_battery_turn_on_does_not_auto_suspend():
    assert G.allows_auto_suspend_for_reassert(
        kind="tablet",
        target_service="turn_on",
        battery_pct="unavailable",
        tablet_low=40,
    ) is False
    assert G.allows_auto_suspend_for_reassert(
        kind="tablet",
        target_service="turn_on",
        battery_pct="unknown",
        tablet_low=40,
    ) is False


def test_tablet_low_battery_turn_on_does_not_auto_suspend():
    assert G.allows_auto_suspend_for_reassert(
        kind="tablet",
        target_service="turn_on",
        battery_pct=35,
        tablet_low=40,
    ) is False


def test_tablet_not_needing_charge_allows_auto_suspend():
    assert G.allows_auto_suspend_for_reassert(
        kind="tablet",
        target_service="turn_off",
        battery_pct=85,
        tablet_low=40,
    ) is True
    assert G.allows_auto_suspend_for_reassert(
        kind="tablet",
        target_service="turn_on",
        battery_pct=60,
        tablet_low=40,
    ) is True


def test_appliance_unknown_power_still_allows_auto_suspend_guard():
    assert G.allows_auto_suspend_for_reassert(
        kind="appliance",
        target_service="turn_on",
        battery_pct="unknown",
        tablet_low=40,
    ) is True


def test_ao_turn_on_never_auto_suspends_recovery():
    assert G.allows_auto_suspend_for_reassert(
        kind="generic",
        target_service="turn_on",
        battery_pct="unknown",
        tablet_low=40,
        policy="AO",
    ) is False


def test_cs_turn_on_never_auto_suspends_recovery():
    assert G.allows_auto_suspend_for_reassert(
        kind="generic",
        target_service="turn_on",
        battery_pct=None,
        tablet_low=40,
        policy="CS",
    ) is False


def test_ao_opposite_direction_keeps_non_latching_guard():
    assert G.allows_auto_suspend_for_reassert(
        kind="generic",
        target_service="turn_off",
        battery_pct=None,
        tablet_low=40,
        policy="AO",
    ) is True
