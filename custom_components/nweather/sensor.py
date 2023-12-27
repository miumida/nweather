"""Support for nweather service."""
import logging
import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.weather import WeatherEntity

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.entity import generate_entity_id

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,

    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,

    DOMAIN as SENSOR_DOMAIN,
    Forecast,
    WeatherEntityFeature,
)

from homeassistant.const import (
    TEMP_CELSIUS, UnitOfSpeed, EntityCategory
)

from .const import DOMAIN, VERSION, BSE_URL, CONF_RGN_CD, CONDITIONS, ATTR_O3, ATTR_O3_GRADE, O3_LVL, ATTR_NOW

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant,config_entry: ConfigEntry,async_add_entities,) -> None:
    """Add a weather entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []

    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'wetrTxt') ]
    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'tmpr') ]
    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'humd') ]
    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'stmpr') ]
    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'ytmpr') ]

    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'uv') ]

    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'stationPM10Legend1') ]
    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'stationPM25Legend1') ]
    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'stationKhaiLegend1') ]

    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'stationName') ]

    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'oneHourRainAmt') ]

    entities += [ NaverWeatherSensor(coordinator, config_entry.data, 'news1') ]

    async_add_entities(entities)

class NaverWeatherSensor(CoordinatorEntity, SensorEntity):

    

    def __init__(self, coordinator, config, id):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config
        self._id    = id

        self.entity_id = generate_entity_id('nweather.nweather_{}', '{}_{}'.format(self._config[CONF_RGN_CD], self._id.lower()), hass= self.coordinator.data.hass)
        self._name = None

        self._attr_entity_category = ATTR_NOW[self._id][3]


    @property
    def unique_id(self):
        """Return the entity ID."""
        return f"weather.nweather_{self._config[CONF_RGN_CD]}_{self._id}"


    @property
    def name(self):
        """Return the name of the sensor."""
        self._name = self.coordinator.data.get_name(self._id)

        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this sensor."""
        unit = ATTR_NOW[self._id][1]
        if unit != "":
            return unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ATTR_NOW[self._id][2]

    @property
    def state(self):
        """Return the weather state."""
        fcast = self.coordinator.data.get_state(self._id)

        return fcast

    @property
    def device_class(self):
        if ATTR_NOW[self._id][4] != "":
            return ATTR_NOW[self._id][4]

    @property
    def extra_state_attributes(self):
        """Attributes."""

        attr = self.coordinator.data.get_attr(self._id)

        return attr

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            #"connections": {(self.area, self.unique_id)},
            "identifiers": {
                (
                    DOMAIN,
                    self._config[CONF_RGN_CD],
                )
            },
            "manufacturer": "Naver Weather",
            "model": f"네이버날씨v2",
            "name": f"{self._name} 날씨",
            "sw_version": VERSION,
            "via_device": (DOMAIN, self._config[CONF_RGN_CD]),
            "configuration_url": BSE_URL.format(self._config[CONF_RGN_CD]),
        }
