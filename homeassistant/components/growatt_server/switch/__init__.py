"""Switch actions for growatt inveters."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry

# from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Switch Entities."""
    # config = {**config_entry.data}
    # username = config[CONF_USERNAME]
    # password = config[CONF_PASSWORD]
    # url = config.get{CONF_URL, DEFAULT_URL}
    async_add_entities([GrowattSwitch()])


class GrowattSwitch(SwitchEntity):
    """Representation of a switch-like Growatt Setting."""

    _attr_has_entity_name = True
    _is_on = False

    def __init__(self) -> None:
        """Initialize switch object."""
        super().__init__()
        self._attr_unique_id = "growatt-test-switch"
        self.entity_description = SwitchEntityDescription(
            key="test",
            device_class=SwitchDeviceClass.SWITCH,
            has_entity_name=True,
            name="test",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn switch on."""
        self._is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn switch off."""
        self._is_on = False

    @property
    def is_on(self) -> bool | None:
        """Return the state of the switch."""
        return self._is_on
