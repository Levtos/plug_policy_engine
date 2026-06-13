"""Standalone Home Assistant integration for Plug Policy Engine."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from ._spec import SPEC
from .const import (
    DATA_ENTRIES,
    DATA_SERVICES_REGISTERED,
    DATA_WS_REGISTERED,
    DOMAIN,
    LEGACY_GLOBAL_SOURCE_MAP,
    MODULE_ID,
    service_name,
)
from .coordinator import PlugPolicyCoordinator
from .entities import async_get_entities  # re-export
from .flow import ConfigFlowHelper, OptionsFlowHelper  # re-export
from .services_impl import SERVICES  # re-export
from .view import async_remove_view, async_setup_view
from .websocket_api import async_setup_websocket_api

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

__all__ = [
    "SPEC",
    "SERVICES",
    "ConfigFlowHelper",
    "OptionsFlowHelper",
    "async_setup",
    "async_setup_entry",
    "async_unload_entry",
    "async_get_entities",
]


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    hass.data.setdefault(
        DOMAIN,
        {
            DATA_ENTRIES: {},
            DATA_SERVICES_REGISTERED: False,
            DATA_WS_REGISTERED: False,
        },
    )
    await _async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(
        DOMAIN,
        {
            DATA_ENTRIES: {},
            DATA_SERVICES_REGISTERED: False,
            DATA_WS_REGISTERED: False,
        },
    )
    coord = PlugPolicyCoordinator(hass, entry)
    await coord.async_init()

    bucket = hass.data[DOMAIN][DATA_ENTRIES].setdefault(entry.entry_id, {})
    bucket["module_id"] = MODULE_ID
    bucket["coordinator"] = coord

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_view(hass)
    if not hass.data[DOMAIN].get(DATA_WS_REGISTERED):
        async_setup_websocket_api(hass)
        hass.data[DOMAIN][DATA_WS_REGISTERED] = True
    entry.async_on_unload(entry.add_update_listener(_async_reload_on_options))
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate retired YAML/media-context globals to current Core sources."""
    changed = False
    data = dict(entry.data)
    options = dict(entry.options)
    for target in (data, options):
        for key, value in list(target.items()):
            if isinstance(value, str) and value in LEGACY_GLOBAL_SOURCE_MAP:
                target[key] = LEGACY_GLOBAL_SOURCE_MAP[value]
                changed = True

    if changed or entry.version < 2:
        hass.config_entries.async_update_entry(
            entry,
            data=data,
            options=options,
            version=2,
        )
        _LOGGER.info("Migrated plug_policy_engine globals to Core/Media State")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    bucket = hass.data.get(DOMAIN, {}).get(DATA_ENTRIES, {}).pop(entry.entry_id, None)
    coord: PlugPolicyCoordinator | None = bucket.get("coordinator") if bucket else None
    if coord is not None:
        await coord.async_shutdown()
    if not hass.data.get(DOMAIN, {}).get(DATA_ENTRIES):
        async_remove_view(hass)
    return True


async def _async_reload_on_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_register_services(hass: HomeAssistant) -> None:
    if hass.data[DOMAIN].get(DATA_SERVICES_REGISTERED):
        return

    for action, sdef in SERVICES.items():
        full = service_name(MODULE_ID, action)
        if hass.services.has_service(DOMAIN, full):
            continue

        async def _handle(call: ServiceCall, _handler=sdef.handler):
            return await _handler(hass, call)

        hass.services.async_register(DOMAIN, full, _handle, schema=sdef.schema)
        _LOGGER.debug("registered service %s.%s", DOMAIN, full)

    hass.data[DOMAIN][DATA_SERVICES_REGISTERED] = True
