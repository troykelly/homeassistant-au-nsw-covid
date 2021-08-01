"""NSW Covid 19 Data"""
from datetime import timedelta
import logging

import async_timeout

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_EVENT,
    CONF_MONITORED_CONDITIONS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify

from . import DOMAIN
from .const import (
    ATTR_LOCALLY_ACTIVE,
    ATTR_INTERSTATE_ACTIVE,
    ATTR_OVERSEAS_ACTIVE,
    ATTR_TOTAL_ACTIVE,
    ATTR_LAST_24_HOURS_KNOWN,
    ATTR_LAST_24_HOURS_UNKNOWN,
    ATTR_LAST_24_HOURS_INTERSTATE,
    ATTR_LAST_24_HOURS_OVERSEAS,
    ATTR_LAST_24_HOURS_TOTAL,
    ATTR_LAST_24_HOURS_TESTS,
    ATTR_THIS_WEEK_KNOWN,
    ATTR_THIS_WEEK_UNKNOWN,
    ATTR_THIS_WEEK_INTERSTATE,
    ATTR_THIS_WEEK_OVERSEAS,
    ATTR_THIS_WEEK_TOTAL,
    ATTR_THIS_WEEK_TESTS,
    ATTR_LAST_WEEK_KNOWN,
    ATTR_LAST_WEEK_UNKNOWN,
    ATTR_LAST_WEEK_INTERSTATE,
    ATTR_LAST_WEEK_OVERSEAS,
    ATTR_LAST_WEEK_TOTAL,
    ATTR_LAST_WEEK_TESTS,
    ATTR_THIS_YEAR_KNOWN,
    ATTR_THIS_YEAR_UNKNOWN,
    ATTR_THIS_YEAR_INTERSTATE,
    ATTR_THIS_YEAR_OVERSEAS,
    ATTR_THIS_YEAR_TOTAL,
    ATTR_THIS_YEAR_TESTS,
    ATTR_LAST_24_HOURS_FIRST_DOSE,
    ATTR_LAST_24_HOURS_SECOND_DOSE,
    ATTR_LAST_24_HOURS_TOTAL_DOSE,
    ATTR_TOTAL_FIRST_DOSE,
    ATTR_TOTAL_SECOND_DOSE,
    ATTR_TOTAL_TOTAL_DOSE,
    DEVICE_CLASS_COVID_CASES,
    DEVICE_CLASS_COVID_VACCINATIONS,
    NSWHEALTH_NAME,
    MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)
SCAN_INTERVAL = DEFAULT_SCAN_INTERVAL

TIMESTAMP_TYPES = ["nswcoviddate", "date", "time", "datetime"]


async def async_setup_entry(hass: HomeAssistantType, entry, async_add_entities):
    """Configure a dispatcher connection based on a config entry."""

    api = hass.data[DOMAIN][entry.entry_id]

    if not "entity_ref" in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entity_ref"] = {}

    if not "tasks" in hass.data[DOMAIN]:
        hass.data[DOMAIN]["tasks"] = {}

    entities = []
    for statistic_id in api.statistics:
        statistic = api.statistics[statistic_id]
        if statistic:
            hass.data[DOMAIN]["entity_ref"][statistic.id] = NSWCovidEntry(statistic)
            entities.append(hass.data[DOMAIN]["entity_ref"][statistic.id])

    def device_event_handler(event_type=None, device_id=None, device=None, ts=None):
        if not (event_type and device):
            _LOGGER.warning("Event received with no type or device")
            return None
        _LOGGER.debug("%s event received: %d", event_type, device_id)
        try:
            hass.data[DOMAIN]["entity_ref"][device.id].async_device_changed()
        except Exception as err:
            _LOGGER.error("Unable to send update to HA")
            _LOGGER.exception(err)
            raise err

    async_add_entities(entities)

    hass.data[DOMAIN]["tasks"]["device_tracker"] = api.track(
        interval=SCAN_INTERVAL, event_receiver=device_event_handler
    )


class NSWCovidEntry(RestoreEntity):
    """Represent a NSW Covid Statistic."""

    def __init__(
        self,
        statistic,
    ):
        """Set up NSW Covid entity."""
        self.__statistic = statistic

    def async_device_changed(self):
        """Send changed data to HA"""
        _LOGGER.debug("%s (%d) advising HA of update", self.name, self.unique_id)
        self.async_schedule_update_ha_state()

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        try:
            return self.__statistic.iconId
        except AttributeError:
            return "mdi:virus-outline"

    @property
    def name(self):
        """Return the name of the device."""
        if not self.__statistic.name:
            return None
        return f"{NSWHEALTH_NAME} {self.__statistic.name}"

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self.__statistic.id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement"""
        if (
            self.__statistic.typeName
            and self.__statistic.typeName is not None
            and self.__statistic.typeName in TIMESTAMP_TYPES
        ):
            return "ISO8601"
        return self.__statistic.unit

    @property
    def state(self):
        """Return the sensor state"""
        _LOGGER.debug(
            "%s returning state: %s", self.__statistic.id, self.__statistic.status
        )
        if not self.__statistic.status:
            return None
        if self.__statistic.typeName in TIMESTAMP_TYPES:
            return self.__statistic.status.isoformat()
        if self.__statistic.typeName == "integer":
            return int(self.__statistic.status)
        if self.__statistic.typeName == "float":
            return float(self.__statistic.status)
        return self.__statistic.status

    @property
    def device_class(self):
        """Return the device class if relevent"""
        if (
            self.__statistic.typeName
            and self.__statistic.typeName is not None
            and self.__statistic.typeName in TIMESTAMP_TYPES
        ):
            return "timestamp"
        return None

    async def async_update(self):
        """Update NSW Covid Data"""
        await self.__statistic.refresh()

    async def async_added_to_hass(self):
        """Register state update callback."""
        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        await super().async_will_remove_from_hass()