"""nweather Sensor for Homeassistant."""
import asyncio
import logging
import re
import json

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.helpers.entity import generate_entity_id

from homeassistant.const import (
    Platform,
)

from .const import DOMAIN, CONF_RGN_CD, BSE_URL, VAR_SUMMARY, VAR_API, VAR_HOURLY, ATTR_NOWFCAST, ATTR_HDAYFCAST, ATTR_AIRFCAST, ATTR_SUNRISE, ATTR_SUNSET, ATTR_NOW
from .const import ATTR_UV, ATTR_GRADE, ATTR_LBTXT, ATTR_GTXTS, ATTR_GTXTD

PLATFORMS = [Platform.WEATHER, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up nweather from a config entry."""

    weather_data = NaverWeatherData(hass, config_entry.data)

    async def _async_update_data():
        """Fetch data from nweather."""
        try:
            return await weather_data.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_async_update_data,
        update_interval=timedelta( seconds=600 ),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    config_entry.async_on_unload(config_entry.add_update_listener(async_update_entry))

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def async_update_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Reload nweather component when options changed."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class NaverWeatherData:
    """Keep data for nweather entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config

        self._entity_id = generate_entity_id('nweather.nweather_{}', self._config[CONF_RGN_CD], hass= hass)

        self._weather_data = None
        self.nowFcast_data = {}
        self.hdayFcastList = []

        self.uv       = {}
        self.airFcast = {}
        
        self.daily_forecast = None
        self.hourly_forecast = []

        self._newsCards = []

        self.sunrise = None
        self.sunset  = None


    def get_attr(self, id):
        attr = {}

        if id == "uv":
            attr = { ATTR_LBTXT  : self.uv[ATTR_LBTXT]
                    , ATTR_GRADE : self.uv[ATTR_GRADE]
                    , ATTR_GTXTS : self.uv[ATTR_GTXTS]
                }
        else:
            attr = {}

        return attr

    def get_state(self, id):
        state = ""

        if id == "uv":
            state = self.uv[ATTR_LBTXT]
        elif id == "wetrTxt" or id == "tmpr" or id == "humd" or id == "stmpr" or id == "ytmpr" or id == "oneHourRainAmt" :
            state = self.nowFcast_data[id]
        elif id == "stationPM10" or id == "stationPM25" or id == "stationPM10Legend1" or id =="stationPM25Legend1" or id == "stationKhaiLegend1" or id == "stationName":
            state = self.airFcast[id]
        elif id == "news1" :
            state = self._newsCards[0]["title"]
        else:
            state = ""

        return state

    def get_name(self, id):
        name = ""

        if id == "news1" :
            name = self._newsCards[0]["officeHname"]
        else:
            name = ATTR_NOW[id][0]

        return name
        

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        html = await self.getNweather(async_get_clientsession(self.hass), self._config[CONF_RGN_CD])

        blockApiResult = self.str2Json(VAR_API, html)        

        #weatherSummary = self.str2Json(VAR_SUMMARY, html)
        choiceResult = blockApiResult["results"]["choiceResult"]
        weatherSummary = choiceResult["nowSynthesisFcast~~1"]
        
        domesticWeeklyFcastList = choiceResult["weeklyFcast~~1"]["domesticWeeklyFcastList"]

        _LOGGER.error(weatherSummary);

        self.nowFcast_data = weatherSummary[ATTR_NOWFCAST]
        self.hdayFcastList = domesticWeeklyFcastList

        lifeIndexData = choiceResult["lifeIndex~~1"]

        for item in lifeIndexData:
            clickCode = item["lifeIndexData"]["clickCode"]

            if (clickCode == "uvindx"):
                self.uv = item["lifeIndexData"]

        self.airFcast = weatherSummary[ATTR_AIRFCAST]

        sunRiseSet = choiceResult["sunRiseSet~~1"]["sunRiseSetList"][0]

        self.sunrise = sunRiseSet[ATTR_SUNRISE]
        self.sunset  = sunRiseSet[ATTR_SUNSET]

        self.hourly_forecast = choiceResult["hourlyFcast~~1"]["domesticHourlyFcastList"]

        self._newsCards = choiceResult["newsTodayList~~1"]["newsCards"]["News"]

        #_LOGGER.error(self.nowFcast_data["stmpr"])

        return self


    async def getNweather(self, session, rgnCd):
        """Update function for updating api information."""
        try:
            hdr = {
                    "User-Agent": (
                        "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/78.0.3904.70 safari/537.36"
                    ),
                    "Referer": (
                        "https://naver.com"
                    )
                }

            url = BSE_URL.format(rgnCd)

            res = await session.get(url, headers=hdr, timeout=60)
        
            html = await res.text()
            #_LOGGER.error(html)
            return html
        except Exception as ex:
            _LOGGER.error(f'[{DOMAIN}] Failed to update nweather API status Error: %s', ex)


    def str2Json(self, reg, html):
        try:
            matches = re.findall(reg, html)
            #_LOGGER.error(matches)
            varStr = re.findall(r"{[^;]+}", matches[0])[0]

            rslt = json.loads(varStr)
            #_LOGGER.error(varStr)

            return rslt
        except Exception as ex:
            _LOGGER.error(f'[{DOMAIN}] Failed to update nweather str2Json Error: %s', ex)
            return {}

    def arr2Json(self, reg, html):
        rslt = []
        try:
            matches = re.findall(reg, html)
                    
            varArr = re.findall(r"\[[^;]+\]", matches[0])[0]
            
            for item in json.loads(varArr):
                rslt.append( item )

            return rslt
        except Exception as ex:
            _LOGGER.error(f'[{DOMAIN}] Failed to update nweather arr2Json Error: %s', ex)
            return []
