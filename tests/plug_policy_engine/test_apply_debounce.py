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
