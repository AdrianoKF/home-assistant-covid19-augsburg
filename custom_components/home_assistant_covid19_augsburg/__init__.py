"""The covid19_augsburg component."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .crawler import CovidCrawler, IncidenceData

_LOGGER = logging.getLogger(__name__)

__version__ = "0.1.0"

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Coronavirus Augsburg component."""
    # Make sure coordinator is initialized.
    coordinator = await get_coordinator(hass)

    async def handle_refresh(call):
        _LOGGER.info("Refreshing Coronavirus Augsburg data...")
        await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, "refresh", handle_refresh)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Coronavirus Augsburg from a config entry."""

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, cmp)
                for cmp in PLATFORMS
            ]
        )
    )

    return unload_ok


async def get_coordinator(hass: HomeAssistant):
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    """Get the data update coordinator."""
    if DOMAIN in hass.data:
        return hass.data[DOMAIN]

    async def async_get_data() -> IncidenceData:
        crawler = CovidCrawler(hass)
        return await crawler.crawl()

    hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_data,
        update_interval=timedelta(hours=1),
    )
    await hass.data[DOMAIN].async_refresh()
    return hass.data[DOMAIN]
