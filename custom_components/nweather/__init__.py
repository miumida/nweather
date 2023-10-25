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

from .const import DOMAIN, CONF_RGN_CD, BSE_URL, VAR_SUMMARY, ATTR_NOWFCAST, ATTR_AIRFCAST, ATTR_SUNRISE, ATTR_SUNSET, ATTR_UV

PLATFORMS = [Platform.WEATHER]

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
    """Keep data for Met Éireann weather entities."""

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
        self.hourly_forecast = None

        self.sunrise = None
        self.sunset  = None

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        html = await self.getNweather(async_get_clientsession(self.hass), self._config[CONF_RGN_CD])

        weatherSummary = self.str2Json(VAR_SUMMARY, html)

        self.nowFcast_data = weatherSummary[ATTR_NOWFCAST]
        self.hdayFcastList = weatherSummary["hdayFcastList"]

        self.uv = weatherSummary[ATTR_UV]

        self.airFcast = weatherSummary[ATTR_AIRFCAST]

        self.sunrise = weatherSummary[ATTR_SUNRISE]
        self.sunset  = weatherSummary[ATTR_SUNSET]

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

            return html
        except Exception as ex:
            _LOGGER.error(f'[{DOMAIN}] Failed to update nweather API status Error: %s', ex)


    def str2Json(self, reg, html):
        try:
            matches = re.findall(reg, html)
                    
            varStr = re.findall(r"{[^;]+}", matches[0])[0]

            rslt = json.loads(varStr)
            #_LOGGER.error(rslt)

            return rslt
        except Exception as ex:
            _LOGGER.error(f'[{DOMAIN}] Failed to update nweather str2Json Error: %s', ex)
            return {}
