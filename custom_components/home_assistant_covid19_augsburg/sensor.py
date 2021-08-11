from dataclasses import asdict

from homeassistant.helpers.entity import Entity

from . import get_coordinator


async def async_setup_entry(hass, _, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    coordinator = await get_coordinator(hass)

    async_add_entities(
        [
            CoronaAugsburgSensor(coordinator),
            CoronaAugsburgVaccinationSensor(coordinator),
        ]
    )


class CoronaAugsburgSensor(Entity):
    """Representation of a county with Corona cases."""

    def __init__(self, coordinator):
        """Initialize sensor."""
        self.coordinator = coordinator
        self._name = "Coronavirus Augsburg"
        self._state = None

    @property
    def available(self):
        return self.coordinator.last_update_success and self.coordinator.data

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._name

    @property
    def icon(self):
        return "mdi:biohazard"

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def state(self):
        return self.coordinator.data["incidence"].incidence

    @property
    def device_state_attributes(self):
        data = self.coordinator.data["incidence"]
        return asdict(data)

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)


class CoronaAugsburgVaccinationSensor(Entity):
    """Representation of vaccination data for the city of Augsburg"""

    def __init__(self, coordinator):
        """Initialize sensor."""
        self.coordinator = coordinator
        self._name = "COVID-19 Vaccinations Augsburg"
        self._state = None

    @property
    def available(self):
        return self.coordinator.last_update_success and self.coordinator.data

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._name

    @property
    def icon(self):
        return "mdi:needle"

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def state(self):
        return self.coordinator.data["vaccination"].total_vaccinations

    @property
    def device_state_attributes(self):
        data = self.coordinator.data["vaccination"]
        return asdict(data)

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)
