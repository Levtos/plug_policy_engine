"""Auto-detection helpers for the Plug Policy add/edit device flow.

When the user picks ``switch.living_pc_plug`` we derive the base slug
``living_pc_plug`` and look in ``hass.states`` for canonical sister
entities so the user does not have to type IDs:

- ``sensor.<slug>_power``    → power_entity suggestion
- ``sensor.<slug>_battery``  → battery_entity suggestion (mainly tablets)

Voltage/current/energy are commonly present but the policy engine does
not act on them — they're surfaced in the result as "siblings" so the
flow can mention them in the description without forcing extra inputs.

Pure logic; no homeassistant imports at module level. ``hass`` is duck-
typed (anything that exposes ``states.async_entity_ids()`` works).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SensorSuggestion:
    """Result of an auto-detection pass for one switch entity."""

    base_slug: str
    power_entity: str | None
    battery_entity: str | None
    siblings: tuple[str, ...]  # voltage/current/energy if present (informational)


@dataclass(frozen=True)
class ProfileDevice:
    """One profile-specific device prefill candidate."""

    name: str
    switch_entity: str
    policy: str
    kind: str
    values: dict


# Priority is significant — Einhornzentrale wires every plug through an
# `_atomic` aggregator entity that smooths the raw power reading, so we
# prefer that over the underlying raw sensor. Battery follows the same
# convention. Raw `_power`/`_battery` stay as canonical fallback so
# vanilla setups still get a useful suggestion.
_SUFFIX_POWER = ("_power_atomic", "_power", "_active_power", "_power_w")
_SUFFIX_BATTERY = (
    "_battery_atomic", "_battery", "_battery_level", "_battery_percent",
)
_SUFFIX_SIBLINGS = (
    "_voltage", "_current", "_energy", "_energy_total", "_today_energy",
)


def base_slug(switch_entity: str | None) -> str | None:
    """Strip the domain prefix from ``switch.living_pc_plug`` → ``living_pc_plug``.

    Returns None for empty input. If no dot is present the input is
    treated as a slug already so users typing a partial value still get
    suggestions.
    """
    if not switch_entity:
        return None
    s = switch_entity.strip()
    if not s:
        return None
    return s.split(".", 1)[1] if "." in s else s


def _entity_ids(hass, domain: str | None = "sensor") -> list[str]:
    """Return entity_ids known to HA, optionally limited to one domain.

    Falls back to an empty list if hass exposes no states API (tests).
    """
    states = getattr(hass, "states", None)
    if states is None:
        return []
    # Prefer async_entity_ids when present; otherwise list states.
    aei = getattr(states, "async_entity_ids", None)
    if callable(aei):
        try:
            return list(aei(domain)) if domain is not None else list(aei())
        except TypeError:
            all_ids = list(aei())
            if domain is None:
                return all_ids
            return [eid for eid in all_ids if eid.startswith(f"{domain}.")]
    listing = getattr(states, "async_all", None)
    if callable(listing):
        all_ids = [s.entity_id for s in listing()]
        if domain is None:
            return all_ids
        return [eid for eid in all_ids if eid.startswith(f"{domain}.")]
    return []


def _has_entity(hass, entity_id: str | None) -> bool:
    """Return True when an entity_id is known to HA."""
    if not entity_id:
        return False
    domain = entity_id.split(".", 1)[0] if "." in entity_id else None
    return entity_id in _entity_ids(hass, domain)


def _first_match(candidates: list[str], slug: str, suffixes: tuple[str, ...]) -> str | None:
    """Return the first sensor whose object_id == ``<slug><suffix>``.

    The order in ``suffixes`` is significance order — ``_power`` wins
    over ``_active_power`` when both exist, matching what most plug
    integrations expose.
    """
    by_object: dict[str, str] = {}
    for eid in candidates:
        _, _, obj = eid.partition(".")
        by_object[obj] = eid
    for suf in suffixes:
        eid = by_object.get(f"{slug}{suf}")
        if eid:
            return eid
    return None


def suggest_for_switch(hass, switch_entity: str | None) -> SensorSuggestion:
    """Pure suggestion pass; never raises, always returns a result.

    The caller decides whether to apply the result as a *default* in
    the form schema. Never override an explicit user value.
    """
    slug = base_slug(switch_entity)
    if not slug:
        return SensorSuggestion(base_slug="", power_entity=None, battery_entity=None, siblings=())
    sensors = _entity_ids(hass)
    power = _first_match(sensors, slug, _SUFFIX_POWER)
    battery = _first_match(sensors, slug, _SUFFIX_BATTERY)

    by_object = {eid.partition(".")[2]: eid for eid in sensors}
    siblings: list[str] = []
    for suf in _SUFFIX_SIBLINGS:
        eid = by_object.get(f"{slug}{suf}")
        if eid:
            siblings.append(eid)
    return SensorSuggestion(
        base_slug=slug,
        power_entity=power,
        battery_entity=battery,
        siblings=tuple(siblings),
    )


# ---------------------------------------------------------------------------
# Profile/entity prefill.
#
# These are profile defaults, not hard runtime dependencies. The flow filters
# every candidate against hass.states before applying it, so the same code can
# run on Eltern or vanilla HA without storing dead entity IDs.
# ---------------------------------------------------------------------------


_PROFILE_GLOBALS: dict[str, dict[str, tuple[str, ...]]] = {
    "benni": {
        "presence_entity": (
            "sensor.benni_core_state_presence_personal",
            "sensor.benni_core_presence_personal",
        ),
        "bio_entity": (
            "sensor.benni_core_state_bio_state",
            "sensor.benni_core_user_bio_state",
        ),
        "day_entity": (
            "sensor.benni_core_state_day_state",
            "sensor.benni_core_day_state",
        ),
        "media_context_entity": (
            "sensor.benni_media_state_media_context",
            "sensor.benni_media_context_media_context",
        ),
        "entertainment_active_entity": (
            "binary_sensor.benni_media_state_entertainment_active",
            "binary_sensor.benni_media_context_entertainment_active",
        ),
        "activity_entity": (
            "sensor.benni_core_state_activity_state",
            "sensor.context_activity_state_combined",
            "sensor.benni_context_activity_state",
        ),
    },
}


def profile_global_prefill(hass, profile: str = "benni") -> dict:
    """Return existing global selector defaults for a profile.

    Preference order is significant: standalone/profile-aware integrations win
    over legacy umbrella entities.
    """
    out: dict = {}
    for key, candidates in _PROFILE_GLOBALS.get(profile, {}).items():
        for entity_id in candidates:
            if _has_entity(hass, entity_id):
                out[key] = entity_id
                break
    return out


# ---------------------------------------------------------------------------
# Kind-aware field visibility.
#
# We keep the engine fully tolerant of missing keys — the schema controls
# only what the user *sees*. ``visible_fields_for_kind`` returns the
# concrete CONF_* keys that should appear in the "advanced" step for a
# given kind/policy combination. The basics step (name/switch/policy/
# kind) is always shown; the sensors step is always shown.
# ---------------------------------------------------------------------------


# Field group definitions, expressed as raw CONF strings so this file
# stays HA-free.
_COMMON_POWER_FIELDS = (
    "active_threshold",
    "idle_threshold",
    "deadband_lower",
    "deadband_upper",
    "stable_off_seconds",
    "unknown_behavior",
    "never_cut_when_active",
    "manual_on_cooldown_seconds",
)
_TABLET_FIELDS = ("tablet_low", "tablet_high", "manual_on_cooldown_seconds")
_DIFFUSER_FIELDS = (
    "diffuser_on_minutes", "diffuser_off_minutes", "manual_on_cooldown_seconds",
)
_DOCK_FIELDS = _COMMON_POWER_FIELDS + ("wake_signal_only",)


def advanced_fields_for_kind(kind: str, policy: str) -> tuple[str, ...]:
    """Return the CONF_* keys to render on the advanced step.

    Engine logic is unchanged regardless of what we render — missing
    keys fall back to defaults inside engine.py.
    """
    k = (kind or "generic").lower()
    if k == "tablet":
        fields: tuple[str, ...] = _TABLET_FIELDS
    elif k == "diffuser":
        fields = _DIFFUSER_FIELDS
    elif k == "h14_dock":
        fields = _DOCK_FIELDS
    else:
        # pc, denon, appliance, coffee_maker, bias_light, generic
        fields = _COMMON_POWER_FIELDS
    # allowed_contexts is only meaningful for Schedule-Context policy.
    if (policy or "").upper() == "SC":
        fields = fields + ("allowed_contexts",)
    return fields


def sensors_for_kind(kind: str) -> tuple[str, ...]:
    """Sensor fields shown on the "sensors" step for a given kind."""
    k = (kind or "generic").lower()
    if k == "tablet":
        # A tablet plug usually has both — power for "is being used", battery
        # for charge level; battery is the policy-relevant one.
        return ("power_entity", "battery_entity")
    return ("power_entity",)


# ---------------------------------------------------------------------------
# Device presets for Einhornzentrale's known plug roles.
#
# Each preset gives the canonical safe defaults for one switch slug.
# The flow applies them in the add-path to pre-fill empty slots; user
# edits during the flow are preserved (the flow only sets keys that
# are still missing from the in-progress draft). In the edit-path
# presets are never applied — they only surface as a "preset detected"
# hint in `description_placeholders`.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DevicePreset:
    """Per-slug canonical defaults for a known plug role.

    `label` is a short human-readable phrase shown to the user
    ("PC safe defaults") so they know which preset matched.
    `values` carries the actual CONF_* defaults the flow will fold
    into the draft.
    """

    slug: str
    label: str
    values: dict


# CONF keys are duplicated here as string literals on purpose so this
# helper stays HA-free and import-cycle-free; const.py already pins
# the canonical strings, the tests cross-check them.
_PRESETS: dict[str, DevicePreset] = {
    "living_pc_plug": DevicePreset(
        slug="living_pc_plug",
        label="PC safe defaults",
        values={
            "kind": "pc",
            "active_threshold": 20.0,
            "idle_threshold": 8.0,
            "deadband_lower": 8.0,
            "deadband_upper": 20.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "living_switch_plug": DevicePreset(
        slug="living_switch_plug",
        label="Switch safe defaults",
        values={
            "kind": "generic",
            "active_threshold": 3.0,
            "idle_threshold": 1.0,
            "deadband_lower": 1.0,
            "deadband_upper": 3.0,
            "unknown_behavior": "assume_idle",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "living_ps5_plug": DevicePreset(
        slug="living_ps5_plug",
        label="PS5 safe defaults",
        values={
            "kind": "generic",
            "active_threshold": 10.0,
            "idle_threshold": 3.0,
            "deadband_lower": 3.0,
            "deadband_upper": 10.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "living_tv_plug": DevicePreset(
        slug="living_tv_plug",
        label="TV safe defaults",
        values={
            "kind": "generic",
            "active_threshold": 8.0,
            "idle_threshold": 3.0,
            "deadband_lower": 3.0,
            "deadband_upper": 8.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "living_denon_plug": DevicePreset(
        slug="living_denon_plug",
        label="Denon AVR safe defaults",
        values={
            "kind": "denon",
            "active_threshold": 8.0,
            "idle_threshold": 3.0,
            "deadband_lower": 3.0,
            "deadband_upper": 8.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "living_denon_plug_denon": DevicePreset(
        slug="living_denon_plug_denon",
        label="Denon AVR safe defaults",
        values={
            "kind": "denon",
            "active_threshold": 8.0,
            "idle_threshold": 3.0,
            "deadband_lower": 3.0,
            "deadband_upper": 8.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "wohnbereich_steckdose_tv": DevicePreset(
        slug="wohnbereich_steckdose_tv",
        label="TV safe defaults",
        values={
            "kind": "generic",
            "active_threshold": 8.0,
            "idle_threshold": 3.0,
            "deadband_lower": 3.0,
            "deadband_upper": 8.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
    "kitchen_coffee_machine_plug": DevicePreset(
        slug="kitchen_coffee_machine_plug",
        label="Coffee machine safe defaults",
        values={
            "kind": "coffee_maker",
            "active_threshold": 5.0,
            "idle_threshold": 2.0,
            "deadband_lower": 2.0,
            "deadband_upper": 5.0,
            "unknown_behavior": "assume_idle",
            "never_cut_when_active": True,
            "wake_signal_only": True,
        },
    ),
    "living_subwoofer_plug": DevicePreset(
        slug="living_subwoofer_plug",
        label="Subwoofer (no power sensor)",
        values={
            "kind": "generic",
            "active_threshold": 0.0,
            "idle_threshold": 0.0,
            "deadband_lower": None,
            "deadband_upper": None,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    ),
}

# All three large-appliance plugs share the same conservative preset.
for _slug in (
    "kitchen_washing_machine_plug",
    "kitchen_dryer_plug",
    "kitchen_dishwasher_plug",
):
    _PRESETS[_slug] = DevicePreset(
        slug=_slug,
        label="Major appliance safe defaults",
        values={
            "kind": "appliance",
            "active_threshold": 3.0,
            "idle_threshold": 1.0,
            "deadband_lower": 1.0,
            "deadband_upper": 3.0,
            "unknown_behavior": "assume_active",
            "never_cut_when_active": True,
            "wake_signal_only": False,
        },
    )


def preset_for_switch(switch_entity: str | None) -> DevicePreset | None:
    """Return the canonical preset for a switch_entity, or ``None``.

    Match is on the base slug; the domain prefix is stripped via
    :func:`base_slug`. Tolerant of partial inputs so the flow can probe
    early.
    """
    slug = base_slug(switch_entity)
    if not slug:
        return None
    return _PRESETS.get(slug)


_PROFILE_DEVICES: dict[str, tuple[ProfileDevice, ...]] = {
    "benni": (
        ProfileDevice(
            name="PC",
            switch_entity="switch.living_pc_plug",
            policy="HB",
            kind="pc",
            values={},
        ),
        ProfileDevice(
            name="Denon AVR",
            switch_entity="switch.living_denon_plug_denon",
            policy="HB",
            kind="denon",
            values={"power_entity": "sensor.living_denon_plug_power_atomic"},
        ),
        ProfileDevice(
            name="H14 Pro Dock",
            switch_entity="switch.hall_h14_pro_plug",
            policy="HB",
            kind="h14_dock",
            values={
                "power_entity": "sensor.hall_h14_pro_plug_power",
                "active_threshold": 10.0,
                "idle_threshold": 5.0,
                "deadband_lower": 5.0,
                "deadband_upper": 10.0,
                "unknown_behavior": "assume_active",
                "never_cut_when_active": True,
                "wake_signal_only": False,
            },
        ),
        ProfileDevice(
            name="Waschmaschine",
            switch_entity="switch.kitchen_washing_machine_plug",
            policy="AC",
            kind="appliance",
            values={},
        ),
        ProfileDevice(
            name="Trockner",
            switch_entity="switch.kitchen_dryer_plug",
            policy="AC",
            kind="appliance",
            values={},
        ),
        ProfileDevice(
            name="Spuelmaschine",
            switch_entity="switch.kitchen_dishwasher_plug",
            policy="AC",
            kind="appliance",
            values={},
        ),
        ProfileDevice(
            name="Kaffeevollautomat",
            switch_entity="switch.kitchen_coffee_machine_plug",
            policy="AO",
            kind="coffee_maker",
            values={},
        ),
        ProfileDevice(
            name="Duftstecker Kueche",
            switch_entity="switch.kitchen_diffuser_plug",
            policy="SC",
            kind="diffuser",
            values={"allowed_contexts": ["morning", "day", "evening"]},
        ),
        ProfileDevice(
            name="Bias Light",
            switch_entity="switch.living_bias_light_plug",
            policy="SPECIAL",
            kind="bias_light",
            values={},
        ),
        ProfileDevice(
            name="PS5",
            switch_entity="switch.living_ps5_plug",
            policy="AO",
            kind="generic",
            values={},
        ),
        ProfileDevice(
            name="Nintendo Switch",
            switch_entity="switch.living_switch_plug",
            policy="AO",
            kind="generic",
            values={},
        ),
        ProfileDevice(
            name="OLED TV",
            switch_entity="switch.wohnbereich_steckdose_tv",
            policy="AO",
            kind="generic",
            values={"power_entity": "sensor.living_tv_plug_power_atomic"},
        ),
    ),
}


def profile_device_prefill(hass, profile: str = "benni") -> list[dict]:
    """Return existing profile devices ready to store in the config entry."""
    devices: list[dict] = []
    for item in _PROFILE_DEVICES.get(profile, ()):
        if not _has_entity(hass, item.switch_entity):
            continue
        slug = base_slug(item.switch_entity) or item.switch_entity.replace(".", "_")
        device: dict = {
            "device_id": slug,
            "name": item.name,
            "switch_entity": item.switch_entity,
            "policy": item.policy,
            "kind": item.kind,
        }
        preset = preset_for_switch(item.switch_entity)
        if preset is not None:
            device.update(preset.values)
        device.update(item.values)

        suggestion = suggest_for_switch(hass, item.switch_entity)
        if "power_entity" not in device and suggestion.power_entity:
            device["power_entity"] = suggestion.power_entity
        if "battery_entity" not in device and suggestion.battery_entity:
            device["battery_entity"] = suggestion.battery_entity

        for key in ("power_entity", "battery_entity"):
            if key in device and not _has_entity(hass, device.get(key)):
                device.pop(key)
        devices.append(device)
    return devices
