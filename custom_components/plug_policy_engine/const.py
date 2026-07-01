"""Constants for the standalone Plug Policy Engine integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final[str] = "plug_policy_engine"
MODULE_ID = "plug_policy_engine"
NAME = "Plug Policy Engine"

DATA_ENTRIES: Final[str] = "entries"
DATA_SERVICES_REGISTERED: Final[str] = "services_registered"
DATA_WS_REGISTERED: Final[str] = "ws_registered"

# Kept in ConfigEntry.data so entries migrated from the umbrella module remain
# inspectable with the same marker key.
CONF_MODULE_ID: Final[str] = "_module_id"

# Policy types
POLICY_AO = "AO"          # Always On
POLICY_HB = "HB"          # Home Baseline
POLICY_AC = "AC"          # Away Cut
POLICY_SC = "SC"          # Schedule Context
POLICY_CS = "CS"          # Charging Safe
POLICY_SPECIAL = "SPECIAL"

ALL_POLICIES = [POLICY_AO, POLICY_HB, POLICY_AC, POLICY_SC, POLICY_CS, POLICY_SPECIAL]

# Device kinds
KIND_GENERIC = "generic"
KIND_PC = "pc"
KIND_DENON = "denon"
KIND_H14_DOCK = "h14_dock"
KIND_APPLIANCE = "appliance"
KIND_COFFEE = "coffee_maker"
KIND_BIAS_LIGHT = "bias_light"
KIND_DIFFUSER = "diffuser"
KIND_TABLET = "tablet"
KIND_BLIND = "blind"

ALL_KINDS = [
    KIND_GENERIC, KIND_PC, KIND_DENON, KIND_H14_DOCK, KIND_APPLIANCE,
    KIND_COFFEE, KIND_BIAS_LIGHT, KIND_DIFFUSER, KIND_TABLET, KIND_BLIND,
]

# Config-flow policy selection per kind. The engine already ignores the
# policy for self-contained kinds (they short-circuit on kind); this map
# drives whether/how the flow even asks for a policy.
#   - fixed  → policy is implied; the flow hides the field and sets it.
#   - choice → only a restricted set is meaningful (see below).
#   - free   → any policy (generic/denon/h14_dock); not listed here.
POLICY_FIXED_BY_KIND = {
    KIND_TABLET: POLICY_SPECIAL,
    KIND_BLIND: POLICY_SPECIAL,
    KIND_DIFFUSER: POLICY_SPECIAL,
    KIND_BIAS_LIGHT: POLICY_SPECIAL,
    KIND_PC: POLICY_SPECIAL,
    KIND_COFFEE: POLICY_AO,
}
POLICY_CHOICES_BY_KIND = {
    # AO = never cut + ensure-on: for washer/dryer/dishwasher you must be
    # able to (remote-)start them, so cutting the plug on away is wrong.
    KIND_APPLIANCE: [POLICY_HB, POLICY_AC, POLICY_AO],
}

# Presence (project convention)
PRESENCE_HOME = "zuhause"
PRESENCE_AWAY = "abwesend"
PRESENCE_AT_PARENTS = "bei_eltern"

# Bio
BIO_AWAKE = "awake"
BIO_SLEEP = "sleep"

# Day phases
DAY_MORNING = "morning"
DAY_DAY = "day"
DAY_EVENING = "evening"
DAY_NIGHT = "night"

DAY_PHASE_ALIASES: Final[dict[str, str]] = {
    "early_morning": DAY_MORNING,
    "late_morning": DAY_MORNING,
    "forenoon": DAY_MORNING,
    "afternoon": DAY_DAY,
    "early_evening": DAY_EVENING,
    "late_evening": DAY_EVENING,
    "early_night": DAY_NIGHT,
    "late_night": DAY_NIGHT,
}

# Unknown-power behavior
UNK_ASSUME_ACTIVE = "assume_active"
UNK_ASSUME_IDLE = "assume_idle"

# Desired switch state
DESIRED_ON = "on"
DESIRED_OFF = "off"
DESIRED_KEEP = "keep"

# Config-entry keys
CONF_DEVICES = "devices"
CONF_NAME = "name"
CONF_SWITCH = "switch_entity"
CONF_POWER = "power_entity"
CONF_BATTERY = "battery_entity"
CONF_DISPLAY_ENTITY = "display_entity"   # Tablet: Screen-on/off-Aktor (switch/light/input_boolean)
CONF_POLICY = "policy"
CONF_KIND = "kind"
CONF_ACTIVE_THRESHOLD = "active_threshold"
CONF_IDLE_THRESHOLD = "idle_threshold"
CONF_DEADBAND_LOW = "deadband_lower"
CONF_DEADBAND_HIGH = "deadband_upper"
CONF_STABLE_OFF = "stable_off_seconds"
CONF_UNKNOWN = "unknown_behavior"
CONF_ALLOWED_CONTEXTS = "allowed_contexts"
CONF_NEVER_CUT_ACTIVE = "never_cut_when_active"
CONF_WAKE_SIGNAL_ONLY = "wake_signal_only"
CONF_TABLET_LOW = "tablet_low"
CONF_TABLET_HIGH = "tablet_high"
CONF_DIFFUSER_ON_MIN = "diffuser_on_minutes"
CONF_DIFFUSER_OFF_MIN = "diffuser_off_minutes"
CONF_MANUAL_COOLDOWN = "manual_on_cooldown_seconds"

# Global selectors
CONF_PRESENCE = "presence_entity"
CONF_BIO = "bio_entity"
CONF_DAY = "day_entity"
CONF_MEDIA = "media_context_entity"
CONF_ENTERTAINMENT = "entertainment_active_entity"
CONF_ACTIVITY = "activity_entity"

GLOBAL_PREFILL: Final[dict[str, str]] = {
    CONF_PRESENCE: "sensor.benni_combined_context_presence_personal",
    CONF_BIO: "sensor.benni_combined_context_bio_state",
    CONF_DAY: "sensor.benni_combined_context_day_state",
    CONF_MEDIA: "sensor.benni_media_state_media_context",
    CONF_ENTERTAINMENT: "binary_sensor.benni_media_state_entertainment_active",
    CONF_ACTIVITY: "sensor.benni_combined_context_activity_state",
}

LEGACY_GLOBAL_SOURCE_MAP: Final[dict[str, str]] = {
    "sensor.context_presence_personal_combined": GLOBAL_PREFILL[CONF_PRESENCE],
    "sensor.context_bio_state_combined": GLOBAL_PREFILL[CONF_BIO],
    "sensor.context_day_state_combined": GLOBAL_PREFILL[CONF_DAY],
    "sensor.context_activity_state_combined": GLOBAL_PREFILL[CONF_ACTIVITY],
    "sensor.benni_media_context_media_context": GLOBAL_PREFILL[CONF_MEDIA],
    "binary_sensor.benni_media_context_entertainment_active": GLOBAL_PREFILL[CONF_ENTERTAINMENT],
}

LEGACY_POWER_SOURCE_MAP: Final[dict[str, str]] = {
    "sensor.benni_device_living_pc": "sensor.benni_master_pc",
    "sensor.benni_device_living_avr": "sensor.benni_master_denon",
    "sensor.benni_device_ps5": "sensor.benni_master_ps5",
    "sensor.benni_device_living_switch_plug": "sensor.benni_master_switch",
    "sensor.benni_device_living_tv": "sensor.benni_master_tv",
}

# Behavior
CONF_ENABLE_CONTROL = "enable_control"
CONF_SCAN_INTERVAL = "scan_interval"

STORAGE_VERSION = 1

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_STABLE_OFF = 600
DEFAULT_MANUAL_COOLDOWN = 900
DEFAULT_TABLET_LOW = 40
DEFAULT_TABLET_HIGH = 80
DEFAULT_DIFFUSER_ON = 15
DEFAULT_DIFFUSER_OFF = 15
DEFAULT_ACTIVE_THRESHOLD = 5.0
DEFAULT_IDLE_THRESHOLD = 2.0

# Services
SERVICE_FORCE_EVAL = "force_evaluate"
SERVICE_APPLY_NOW = "apply_policy_now"
SERVICE_SET_ENABLE_CONTROL = "set_enable_control"
SERVICE_SUSPEND = "suspend_device_policy"
SERVICE_RESUME = "resume_device_policy"
SERVICE_MARK_MANUAL = "set_manual_recently_on"

# WebSocket + sidebar panel
WS_GET_STATUS: Final[str] = "plug_policy_engine/get_status"
FRONTEND_DIR_URL: Final[str] = "/plug_policy_engine_static"
FRONTEND_ENTRY: Final[str] = f"{FRONTEND_DIR_URL}/main.js"
PANEL_ELEMENT: Final[str] = "plug-policy-panel"
PANEL_ICON: Final[str] = "mdi:power-plug-outline"
PANEL_TITLE: Final[str] = "Plug Policy"
PANEL_URL_PATH: Final[str] = "plug-policy"


def storage_key(_module_id: str, suffix: str) -> str:
    """Stable Home Assistant storage key for this standalone integration."""
    return f"{DOMAIN}_{suffix}"


def service_name(_module_id: str, action: str) -> str:
    """Standalone service name, e.g. `plug_policy_engine.force_evaluate`."""
    return action


def unique_id(_module_id: str, *parts: str) -> str:
    """Standalone unique_id with integration prefix."""
    return "_".join((DOMAIN, *parts))


def device_dev_id_from_identifier(
    identifier: str, module_id: str, entry_id: str
) -> str | None:
    """Extract the plug_policy device dev_id from a device-registry identifier.

    Per-device identifier = ``<module_id>_<entry_id>_<dev_id>`` (see
    entities._dev_device_info). Returns the dev_id, or ``None`` for the hub
    identifier (``<module_id>_<entry_id>``) or any identifier not belonging to
    this entry. Used to detect/prune stale devices left behind after a device
    is removed from the config.
    """
    prefix = f"{module_id}_{entry_id}"
    if identifier == prefix:
        return None  # hub device
    head = f"{prefix}_"
    if identifier.startswith(head):
        return identifier[len(head):]
    return None
