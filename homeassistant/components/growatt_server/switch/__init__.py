"""Switch actions for growatt inveters."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..growatt import GrowattData, get_device_list, init_growatt_api


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Switch Entities."""

    config = {**config_entry.data}
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    api = await init_growatt_api(hass, config_entry)
    devices, plant_id = await hass.async_add_executor_job(get_device_list, api, config)

    for device in devices:
        probe = GrowattData(
            api, username, password, device["deviceSn"], device["deviceType"]
        )
        if device["deviceType"] == "mix":
            async_add_entities([GrowattSwitch(config_entry, device, probe)])


class GrowattSwitch(SwitchEntity):
    """Representation of a switch-like Growatt Setting."""

    _attr_has_entity_name = True
    _is_on = False

    def __init__(self, config_entry: ConfigEntry, device, probe) -> None:
        """Initialize switch object."""
        super().__init__()

        self._attr_unique_id = f"growatt-test-switch-{config_entry.entry_id}"
        self.entity_description = SwitchEntityDescription(
            key="test",
            device_class=SwitchDeviceClass.SWITCH,
            has_entity_name=True,
            name="test",
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, probe.device_id)},
            "name": f"{device['deviceAilas']}",
            "manufacturer": "Growatt",
        }

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
