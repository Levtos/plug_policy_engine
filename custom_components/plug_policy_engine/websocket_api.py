"""WebSocket API for the Plug Policy observability panel."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import WS_GET_STATUS
from .coordinator import all_plug_policy_coordinators


def _status(hass: HomeAssistant) -> dict[str, Any]:
    coords = all_plug_policy_coordinators(hass)
    if not coords:
        return {
            "global": {
                "enable_control": False,
                "context": {},
                "last_update_ts": None,
            },
            "devices": [],
            "debug_export": {"global": {}, "devices": []},
        }

    first = coords[0].status_snapshot()
    devices: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for coord in coords:
        snap = coord.status_snapshot()
        devices.extend(snap["devices"])
        entries.append(snap["debug_export"])

    global_status = {
        **first["global"],
        "entry_count": len(coords),
    }
    return {
        "global": global_status,
        "devices": devices,
        "debug_export": {
            "global": global_status,
            "devices": devices,
            "entries": entries,
        },
    }


def async_setup_websocket_api(hass: HomeAssistant) -> None:
    @websocket_api.websocket_command({vol.Required("type"): WS_GET_STATUS})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_get_status(hass, connection, msg) -> None:
        connection.send_result(msg["id"], _status(hass))

    websocket_api.async_register_command(hass, ws_get_status)
