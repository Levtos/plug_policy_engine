"""Config and options flow for Plug Policy Engine."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback

from .const import DOMAIN
from .flow import ConfigFlowHelper, OptionsFlowHelper


class PlugPolicyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 10

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        helper = ConfigFlowHelper(self.hass, self)
        if user_input is not None:
            return await helper.async_step_module_step(user_input)
        return await helper.async_step_init()

    async def async_step_module_step(self, user_input: dict[str, Any] | None = None):
        return await ConfigFlowHelper(self.hass, self).async_step_module_step(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> "PlugPolicyOptionsFlow":
        return PlugPolicyOptionsFlow(entry)


class PlugPolicyOptionsFlow(OptionsFlow):
    def __init__(self, entry: ConfigEntry) -> None:
        self.entry = entry
        self._helper: OptionsFlowHelper | None = None

    @property
    def helper(self) -> OptionsFlowHelper:
        if self._helper is None:
            self._helper = OptionsFlowHelper(self.hass, self.entry, self)
        return self._helper

    async def async_step_init(self, user_input=None):
        return await self.helper.async_step_init(user_input)

    async def async_step_globals(self, user_input=None):
        return await self.helper.async_step_globals(user_input)

    async def async_step_prefill_devices(self, user_input=None):
        return await self.helper.async_step_prefill_devices(user_input)

    async def async_step_add_device(self, user_input=None):
        return await self.helper.async_step_add_device(user_input)

    async def async_step_device_basics(self, user_input=None):
        return await self.helper.async_step_device_basics(user_input)

    async def async_step_device_sensors(self, user_input=None):
        return await self.helper.async_step_device_sensors(user_input)

    async def async_step_device_advanced(self, user_input=None):
        return await self.helper.async_step_device_advanced(user_input)

    async def async_step_edit_device(self, user_input=None):
        return await self.helper.async_step_edit_device(user_input)

    async def async_step_remove_device(self, user_input=None):
        return await self.helper.async_step_remove_device(user_input)
