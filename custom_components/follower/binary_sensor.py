"""Binary sensor platform for follower."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import callback

from .const import (
    BINARY_SENSOR,
    BINARY_SENSOR_DEVICE_CLASS,
    DOMAIN,
)


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup binary_sensor platform."""
    entities = []
    for thing in discovery_info["entities"]:
        _LOGGER.error(thing)
        entities.append(FollowerBinarySensor(hass, thing))

    async_add_entities(entities)
    await discovery_info["registrar"](entities)


class FollowerBinarySensor(BinarySensorEntity):
    """follower binary_sensor class."""

    def __init__(self, hass, config_entry):
        self.hass = hass
        self.config_entry = config_entry
        self.int_state = False
        self._unsub_listener = None
        self.hass.async_create_task(self.start())

    async def start(self):
        self._unsub_listener = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED,
            self.listen_handler,
            self.listen_filter,
        )

    async def shutdown(self):
        self._unsub_listener()
        await self.async_remove()

    @callback
    async def listen_handler(self, event):
        new_state = event.data["new_state"].state
        if new_state == "on":
            service_name = "turn_on"
            self.int_state = True
        else:
            service_name = "turn_off"
            self.int_state = False

        _LOGGER.error(
            "Performing %s for %s led by %s",
            service_name,
            self.config_entry["follower"],
            self.config_entry["leader"],
        )

        await self.hass.services.async_call(
            "homeassistant",
            service_name,
            {"entity_id": self.config_entry["follower"]},
        )

        await self.async_update_ha_state()

    @callback
    def listen_filter(self, event):
        if event.data["entity_id"] == self.config_entry["leader"]:
            return True
        return False

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f'{DOMAIN}_{self.config_entry["name"]}'

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.config_entry["name"],
            "model": BINARY_SENSOR,
            "manufacturer": "Device Manu",
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": f"{DOMAIN} {BINARY_SENSOR}",
            "id": str(self.unique_id),
            "integration": DOMAIN,
        }

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return f'{DOMAIN}_{self.config_entry["name"]}'

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BINARY_SENSOR_DEVICE_CLASS

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.int_state
