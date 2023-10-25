"""Support for nweather service."""
import logging
import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.weather import WeatherEntity

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    TEMP_CELSIUS, UnitOfSpeed
)

from .const import DOMAIN, VERSION, BSE_URL, CONF_RGN_CD, CONDITIONS, ATTR_O3, ATTR_O3_GRADE, O3_LVL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant,config_entry: ConfigEntry,async_add_entities,) -> None:
    """Add a weather entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [ NaverWeather(coordinator, config_entry.data) ]

    async_add_entities(entities)


class NaverWeather(CoordinatorEntity, WeatherEntity):
    """Implementation of a Met Éireann weather condition."""

    _attr_native_temperature_unit = TEMP_CELSIUS
    #_attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_supported_features = WeatherEntityFeature.FORECAST_TWICE_DAILY

    def __init__(self, coordinator, config):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config

        self.entity_id = self.coordinator.data._entity_id
        self._name = None

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"weather.nweather_{self._config[CONF_RGN_CD]}"

    @property
    def name(self):
        """Return the name of the sensor."""
        lareaNm      = self.coordinator.data.nowFcast_data.get("lareaNm")
        fullAreaName = self.coordinator.data.nowFcast_data.get("fullAreaName")
        name = f"{lareaNm} {fullAreaName}"

        self._name = name

        return name

    @property
    def condition(self):
        """Return the current condition."""
        now = datetime.datetime.now()

        currentTm = now.strftime('%H%M%S')

        sunSetTm = self.coordinator.data.sunset
        sunRiseTm = self.coordinator.data.sunrise

        fcast = self.coordinator.data.nowFcast_data.get("wetrTxt")

        if '맑음' in fcast and ( currentTm > sunSetTm or currentTm < sunRiseTm ) :
            return CONDITIONS["맑음(밤)"]

        return CONDITIONS[self.coordinator.data.nowFcast_data.get("wetrTxt")]

    @property
    def state(self):
        """Return the weather state."""
        now = datetime.datetime.now()

        currentTm = now.strftime('%H%M%S')

        sunSetTm  = self.coordinator.data.sunset
        sunRiseTm = self.coordinator.data.sunrise

        fcast = self.coordinator.data.nowFcast_data.get("wetrTxt")

        if '맑음' in fcast and ( currentTm > sunSetTm or currentTm < sunRiseTm ) :
            return CONDITIONS["맑음(밤)"]

        return CONDITIONS[self.coordinator.data.nowFcast_data.get("wetrTxt")]

    @property
    def native_apparent_temperature(self):
        """Return the temperature."""
        return self.coordinator.data.nowFcast_data.get("stmpr")

    @property
    def native_temperature(self):
        """Return the temperature."""
        return self.coordinator.data.nowFcast_data.get("tmpr")

    @property
    def humidity(self):
        """Return the humidity."""
        return self.coordinator.data.nowFcast_data.get("humd")

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        return self.coordinator.data.nowFcast_data.get("windSpd")

    @property
    def native_wind_speed_unit(self):
        """Return the wind speed unit."""
        return UnitOfSpeed.METERS_PER_SECOND

    @property
    def wind_bearing(self):
        """Return the wind direction."""
        return self.coordinator.data.nowFcast_data.get("windDrctnName")

    @property
    def ozone(self) -> float | None:
        return float(O3_LVL[self.coordinator.data.airFcast.get(ATTR_O3_GRADE)])

    @property
    def attribution(self):
        """Return the attribution."""
        return "Weather forecast from Naver, Powered by miumida"

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        return self._forecast()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units.
        
        Only implement this method if `WeatherEntityFeature.FORECAST_DAILY` is set
        """
        return self._forecast()

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units.
        
        Only implement this method if `WeatherEntityFeature.FORECAST_DAILY` is set
        """
        return self._forecast()
        

    def _forecast(self) -> list[Forecast] | None:
        forecast = []

        _LOGGER.error(self.coordinator.data.hdayFcastList)

        for data in self.coordinator.data.hdayFcastList:
            dt = datetime.datetime.strptime(data["aplYmd"], '%Y%m%d')
            
            #주간
            next_day = {
                ATTR_FORECAST_TIME: dt,
                ATTR_FORECAST_CONDITION: CONDITIONS[data["amWetrTxt"]],
                ATTR_FORECAST_TEMP_LOW: data["minTmpr"],
                ATTR_FORECAST_TEMP: data["maxTmpr"],
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: data["amRainProb"],
                #ATTR_FORECAST_WIND_BEARING: data[""],
                #ATTR_FORECAST_WIND_SPEED: data[""],
                "is_daytime" : True,
                
                # Not officially supported, but nice additions.
                "condition_am": data["amWetrTxt"],
                "condition_pm": data["pmWetrTxt"],

                "rain_rate_am": data["amRainProb"],
                "rain_rate_pm": data["pmRainProb"]
            }
            forecast.append(next_day)

            #야간
            next_day = {
                ATTR_FORECAST_TIME: dt,
                ATTR_FORECAST_CONDITION: CONDITIONS[data["pmWetrTxt"]],
                ATTR_FORECAST_TEMP_LOW: data["minTmpr"],
                ATTR_FORECAST_TEMP: data["maxTmpr"],
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: data["pmRainProb"],
                #ATTR_FORECAST_WIND_BEARING: data[""],
                #ATTR_FORECAST_WIND_SPEED: data[""],
                "is_daytime" : False,
                
                # Not officially supported, but nice additions.
                "condition_am": data["amWetrTxt"],
                "condition_pm": data["pmWetrTxt"],

                "rain_rate_am": data["amRainProb"],
                "rain_rate_pm": data["pmRainProb"]
            }
            forecast.append(next_day)

        return forecast

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
