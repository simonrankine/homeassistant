"""Read status of growatt inverters."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..growatt import GrowattData, get_device_list, init_growatt_api
from .inverter import INVERTER_SENSOR_TYPES
from .mix import MIX_SENSOR_TYPES
from .sensor_entity_description import GrowattSensorEntityDescription
from .storage import STORAGE_SENSOR_TYPES
from .tlx import TLX_SENSOR_TYPES
from .total import TOTAL_SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Growatt sensor."""
    config = {**config_entry.data}
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    name = config[CONF_NAME]

    api = await init_growatt_api(hass, config_entry)
    devices, plant_id = await hass.async_add_executor_job(get_device_list, api, config)

    probe = GrowattData(api, username, password, plant_id, "total")
    entities = [
        GrowattInverter(
            probe,
            name=f"{name} Total",
            unique_id=f"{plant_id}-{description.key}",
            description=description,
        )
        for description in TOTAL_SENSOR_TYPES
    ]

    # Add sensors for each device in the specified plant.
    for device in devices:
        probe = GrowattData(
            api, username, password, device["deviceSn"], device["deviceType"]
        )
        sensor_descriptions: tuple[GrowattSensorEntityDescription, ...] = ()
        if device["deviceType"] == "inverter":
            sensor_descriptions = INVERTER_SENSOR_TYPES
        elif device["deviceType"] == "tlx":
            probe.plant_id = plant_id
            sensor_descriptions = TLX_SENSOR_TYPES
        elif device["deviceType"] == "storage":
            probe.plant_id = plant_id
            sensor_descriptions = STORAGE_SENSOR_TYPES
        elif device["deviceType"] == "mix":
            probe.plant_id = plant_id
            sensor_descriptions = MIX_SENSOR_TYPES
        else:
            _LOGGER.debug(
                "Device type %s was found but is not supported right now",
                device["deviceType"],
            )

        entities.extend(
            [
                GrowattInverter(
                    probe,
                    name=f"{device['deviceAilas']}",
                    unique_id=f"{device['deviceSn']}-{description.key}",
                    description=description,
                )
                for description in sensor_descriptions
            ]
        )

    async_add_entities(entities, True)


class GrowattInverter(SensorEntity):
    """Representation of a Growatt Sensor."""

    _attr_has_entity_name = True

    entity_description: GrowattSensorEntityDescription

    def __init__(
        self, probe, name, unique_id, description: GrowattSensorEntityDescription
    ) -> None:
        """Initialize a PVOutput sensor."""
        self.probe = probe
        self.entity_description = description

        self._attr_unique_id = unique_id
        self._attr_icon = "mdi:solar-power"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, probe.device_id)},
            manufacturer="Growatt",
            name=name,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        result = self.probe.get_data(self.entity_description)
        if self.entity_description.precision is not None:
            result = round(result, self.entity_description.precision)
        return result

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor, if any."""
        if self.entity_description.currency:
            return self.probe.get_currency()
        return super().native_unit_of_measurement

    def update(self) -> None:
        """Get the latest data from the Growat API and updates the state."""
        self.probe.update()
