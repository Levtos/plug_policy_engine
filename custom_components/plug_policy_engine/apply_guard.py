"""Pure apply-layer guards for the coordinator (HA-free, unit-testable).

Lives outside the HA-coupled coordinator so the command de-bounce decision can
be tested without Home Assistant — same pattern as ``engine.py``.

Background (FLEET-107): a non-latching / flapping plug drops its commanded
state on the device side (no ``turn_off`` is ever called — the plug simply
does not latch). The coordinator sees ``off`` again and re-asserts
``turn_on``. The existing ``_pending_actions`` retry guard does not help,
because the brief ``on`` read in between clears it (``_clear_pending_action_if_reached``),
so commands fire at event-loop speed (~6/s on the diffuser, ~10-20s on the
bias light). The de-bounce below keys off the last *sent* command instead of
whether the target was reached, so it survives that brief read.
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

# Minimum seconds between two *identical* switch commands to the same device.
# Legitimate policy commands for these device kinds are minutes apart
# (diffuser 15/15 cycle, bias light follows entertainment), so a 30s floor
# never suppresses real intent — it only collapses a flap storm.
MIN_COMMAND_INTERVAL_SECONDS = 30.0
NON_LATCH_FAILURE_THRESHOLD = 5
NON_LATCH_WINDOW_SECONDS = 600.0


def debounce_suppresses(
    last_command: Optional[Tuple[str, float]],
    target_service: str,
    now_ts: float,
    interval: float = MIN_COMMAND_INTERVAL_SECONDS,
) -> bool:
    """Return True if sending ``target_service`` now should be suppressed.

    Suppresses only a *repeat* of the same command within ``interval`` seconds.
    A direction change (e.g. ``turn_on`` -> ``turn_off``) always passes, so
    genuine intent — a sleep cut or away cut — is never delayed.
    """
    if not last_command:
        return False
    last_service, last_ts = last_command
    if last_service != target_service:
        return False
    if interval <= 0:
        return False
    return (now_ts - last_ts) < interval


def prune_reassert_history(
    history: Sequence[Tuple[str, float]],
    target_service: str,
    now_ts: float,
    window: float = NON_LATCH_WINDOW_SECONDS,
) -> list[Tuple[str, float]]:
    """Keep recent same-direction re-asserts inside ``window`` seconds."""
    if window <= 0:
        return [(target_service, now_ts)]
    return [
        (service, ts)
        for service, ts in history
        if service == target_service and (now_ts - ts) <= window
    ]


def record_reassert_and_should_suspend(
    history: Sequence[Tuple[str, float]],
    target_service: str,
    now_ts: float,
    *,
    threshold: int = NON_LATCH_FAILURE_THRESHOLD,
    window: float = NON_LATCH_WINDOW_SECONDS,
) -> tuple[list[Tuple[str, float]], bool]:
    """Record a sent command and decide whether the device is non-latching.

    The coordinator calls this only after it actually sends a switch command.
    Repeated same-direction commands to the same entity mean previous commands
    did not latch; after ``threshold`` attempts inside ``window`` we suspend the
    device policy instead of continuing a relay-churn loop.
    """
    recent = prune_reassert_history(history, target_service, now_ts, window)
    recent.append((target_service, now_ts))
    return recent, threshold > 0 and len(recent) >= threshold
