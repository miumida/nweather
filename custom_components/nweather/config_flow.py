"""Config flow for naver_weather."""
import logging
import re
import json

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_RGN_CD, BSE_URL, VAR_SUMMARY, VAR_API, ATTR_NOWFCAST

_LOGGER = logging.getLogger(__name__)

async def getNweather(session, rgnCd):
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

def str2Json(reg, html):
    try:
        matches = re.findall(reg, html)
                
        varStr = re.findall(r"{[^;]+}", matches[0])[0]

        rslt = json.loads(varStr)
        #_LOGGER.error(rslt)

        return rslt
    except Exception as ex:
        _LOGGER.error(f'[{DOMAIN}] Failed to update nweather str2Json Error: %s', ex)
        return {}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Naver Weather."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            area = user_input.get(CONF_RGN_CD, "")
            user_input[CONF_RGN_CD] = area

            await self.async_set_unique_id()
            self._abort_if_unique_id_configured()

            session = async_create_clientsession(self.hass)

            html = await getNweather(session, area)

            blockApiResult = str2Json(VAR_API, html)

            choiceResult = blockApiResult["results"]["choiceResult"]
            weatherSummary = choiceResult["nowSynthesisFcast~~1"]

            #_LOGGER.error(f'[{DOMAIN}] weatherSummary -> {weatherSummary}')

            mareaNm = weatherSummary[ATTR_NOWFCAST]["mareaNm"]
            sareaNm = weatherSummary[ATTR_NOWFCAST]["sareaNm"]

            title_area = f"{mareaNm} {sareaNm}({area})"

            #_LOGGER.error(f'[{DOMAIN}] title_area -> {title_area}')

            return self.async_create_entry(title=title_area, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_RGN_CD): cv.string,
#                    vol.Optional(CONF_TODAY, default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input=None):
        """Handle configuration by yaml file."""
        await self.async_set_unique_id(user_input[CONF_RGN_CD])
        for entry in self._async_current_entries():
            if entry.unique_id == self.unique_id:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
                self._abort_if_unique_id_configured()
        return self.async_create_entry(title=user_input[CONF_RGN_CD], data=user_input)
