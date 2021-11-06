"""
Custom integration for Follower

For more details about this integration, please refer to
blah blah blah
"""
import logging

from homeassistant.core import Config, HomeAssistant, ServiceCall
from homeassistant.config import async_hass_config_yaml
from homeassistant.helpers import discovery

from .const import (
    DOMAIN,
    STARTUP_MESSAGE,
    SERVICE_RELOAD,
    BINARY_SENSOR,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EntityRegistry:
    def __init__(self):
        self.registered_entities = []

    async def register_entities(self, entities):
        for entity in entities:
            self.registered_entities.append(entity)

    async def shutdown(self):
        for entity in self.registered_entities:
            await entity.shutdown()

        self.registered_entities = []


async def async_setup(hass: HomeAssistant, hass_config: Config) -> bool:
    """Component setup."""
    if hass.data.get(DOMAIN) is None:
        _LOGGER.info(STARTUP_MESSAGE)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = hass_config[DOMAIN]

    registry = EntityRegistry()

    await start_it_up(hass, hass_config, registry)

    async def reload_scripts_handler(call: ServiceCall) -> None:
        """Handle reload service calls."""
        _LOGGER.debug("reloading")

        await registry.shutdown()

        conf = await async_hass_config_yaml(hass)
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN] = conf[DOMAIN]
        await start_it_up(hass, conf, registry)

    hass.services.async_register(DOMAIN, SERVICE_RELOAD, reload_scripts_handler)

    return True


async def start_it_up(hass: HomeAssistant, hass_config, registry: EntityRegistry):
    config = {"registrar": registry.register_entities, "entities": hass.data[DOMAIN]}

    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            BINARY_SENSOR,
            DOMAIN,
            config,
            hass_config,
        )
    )
