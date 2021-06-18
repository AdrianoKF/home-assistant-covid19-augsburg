"""Config flow for Coronavirus Augsburg integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Coronavirus Augsburg."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id("augsburg")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="COVID-19 Augsburg", data=user_input)

        _LOGGER.debug("Showing config form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
