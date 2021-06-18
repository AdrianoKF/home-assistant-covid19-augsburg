from homeassistant.helpers.entity import Entity

from . import get_coordinator


async def async_setup_entry(hass, _, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    coordinator = await get_coordinator(hass)

    async_add_entities([CoronaAugsburgSensor(coordinator)])


class CoronaAugsburgSensor(Entity):
    """Representation of a county with Corona cases."""

    def __init__(self, coordinator):
        """Initialize sensor."""
        self.coordinator = coordinator
        self._name = "Coronavirus Augsburg"
        self._state = None

    @property
    def available(self):
        return self.coordinator.last_update_success

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
        return "people"

    @property
    def state(self):
        return self.coordinator.data

    # @property
    # def device_state_attributes(self):
    # return {
    #     "date": self.coordinator.data.date,
    #     "total_cases": self.coordinator.data.total_cases,
    #     "num_dead": self.coordinator.data.num_dead,
    #     "num_recovered": self.coordinator.data.num_recovered,
    #     "num_infected": self.coordinator.data.num_infected,
    #     "incidence": self.coordinator.data.incidence,
    # }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)
