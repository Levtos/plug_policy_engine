"""HA-free spec declaration for Plug Policy Engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


@dataclass(frozen=True)
class ModuleSpec:
    module_id: str
    name: str
    description: str
    status: str
    platforms: tuple[Enum, ...]
    has_services: bool
    icon: str


class ModuleStatus:
    READY = "ready"


class _P(str, Enum):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"


SPEC: Final[ModuleSpec] = ModuleSpec(
    module_id="plug_policy_engine",
    name="Plug Policy Engine",
    description=(
        "Policy-getriebenes Schalten von Steckdosen "
        "(AO/HB/AC/SC/CS/SPECIAL + spezielle Device-Kinds)."
    ),
    status=ModuleStatus.READY,
    platforms=(_P.SENSOR, _P.BINARY_SENSOR),
    has_services=True,
    icon="mdi:power-socket-de",
)
