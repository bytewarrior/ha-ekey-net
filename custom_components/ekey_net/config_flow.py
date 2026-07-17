"""Config and options flow of the ekey net integration.

Initial setup is deliberately minimal (UDP port only). All fine-tuning lives in
the options flow: protocol format override, ekey user -> HA person mapping,
display name fallback and an optional bind address.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_PORT
from homeassistant.core import callback

from .const import (
    CONF_BIND_ADDRESS,
    CONF_NAME_MAP,
    CONF_PROTOCOL_FORMAT,
    CONF_USER_MAP,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    PROTOCOL_AUTO,
    PROTOCOL_FORMATS,
)


class EkeyNetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ekey net."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Initial setup: only choose the UDP receive port."""
        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                        int, vol.Range(min=1, max=65535)
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return EkeyNetOptionsFlow()


class EkeyNetOptionsFlow(OptionsFlow):
    """Fine-tuning: format override and user mapping."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and save the options form."""
        if user_input is not None:
            # Do not persist empty optional fields (keep the default).
            cleaned = {key: value for key, value in user_input.items() if value not in ("", None)}
            return self.async_create_entry(title="", data=cleaned)

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PROTOCOL_FORMAT,
                    default=options.get(CONF_PROTOCOL_FORMAT, PROTOCOL_AUTO),
                ): vol.In(PROTOCOL_FORMATS),
                vol.Optional(
                    CONF_USER_MAP,
                    default=options.get(CONF_USER_MAP, ""),
                ): str,
                vol.Optional(
                    CONF_NAME_MAP,
                    default=options.get(CONF_NAME_MAP, ""),
                ): str,
                vol.Optional(
                    CONF_BIND_ADDRESS,
                    default=options.get(CONF_BIND_ADDRESS, ""),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
