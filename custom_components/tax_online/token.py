"""A demonstration 'token' that connects several devices."""
from __future__ import annotations

# In a real implementation, this would be in an external library that's on PyPI.
# The PyPI package needs to be included in the `requirements` section of manifest.json
# See https://developers.home-assistant.io/docs/creating_integration_manifest
# for more information.
# This dummy token always returns 1 cron.
import asyncio
import json
import random
import requests
from homeassistant.core import HomeAssistant
import logging
from .const import API_KEY, API_IP
_LOGGER = logging.getLogger(__name__)

class Token:
    """Dummy token for Hello World example."""

    manufacturer = "SAFEcert Corp"

    def __init__(self, hass: HomeAssistant, name: str, api_ip_address: str, tax_ids: str, access_token: str, input_config: dict, output_folder: str) -> None:
        """Init dummy token."""

        try:
            input_config["serial_number"]
            input_config["tax_ids"]
            input_config["taikhoanTracuu"]
            input_config["maDoiTuong"]
            input_config["access_token"] = json.dumps(input_config["access_token"])
            input_config["nguoiky"]
            input_config["output_folder"]
        except:
            return True

        serial_number = input_config["serial_number"].upper()
        output_folder = output_folder.upper()
        self._name = name
        self._api_ip_address = api_ip_address
        self._serial_number = serial_number
        self._access_token = json.loads(access_token)
        self._tax_ids = json.loads(tax_ids)

        self._taikhoanTracuu = input_config["taikhoanTracuu"]
        self._maDoiTuong = input_config["maDoiTuong"]
        self._nguoiky = input_config["nguoiky"]
        self._output_folder = output_folder

        self._hass = hass
        self._id = name.replace(" ", "_").lower()
        self._installed = False
        self._is_valid_token = False
        cron_id = f"{self._id}_"+serial_number
        cron_name = "Excel Converter. " + self._name
        self.crons = [
            Crons(cron_id, cron_name, self),
        ]
        self.online = True

    async def check_serial_exists(self):
        requestHeaders = {
            "Content-Type": "application/json",
        }
        requestBody = {
            "pin": self._pin,
            "api_key": API_KEY,
        }
        requestURL = "http://" + self._api_ip_address + ":3000/api/token/getInfo"
        # future = self._loop.run_in_executor(None, requests.post, requestURL, data=json.dumps(requestBody), headers=requestHeaders)
        try:
            response = await self._hass.async_add_executor_job(lambda: requests.post(requestURL, data=json.dumps(requestBody), headers=requestHeaders))
            response = response.json()
        except:
            """"""
            response = {
                "status":1,
                "message":"Could not connect to API or timeout"
            }

        if response:
            if "status" not in response or response["status"] != 0:
                _LOGGER.exception(response["message"])
                self._enable = "off"
            elif "data" in response and "certs" in response["data"]:
                for signature in response["data"]["certs"]:
                    if "SerialNumber" in signature and signature["SerialNumber"] == self._serial_number:
                        self._is_valid_token = True
        
        return self._is_valid_token
            

    @property
    def token_id(self) -> str:
        """ID for dummy token."""
        return self._id

    def installed(self) -> None:
        return self._installed

    def set_installed(self) -> None:
        self._installed = True

class Crons:
    """Dummy cron (device for HA) for Hello World example."""

    def __init__(self, cronid: str, name: str, token: Token) -> None:
        """Init dummy cron."""
        self._id = cronid
        self.token = token
        self.name = name
        self.serial_number = token._serial_number.upper()
        self.access_token = token._access_token
        self.tax_ids = token._tax_ids

        self.taikhoanTracuu = token._taikhoanTracuu
        self.maDoiTuong     = token._maDoiTuong
        self.nguoiky        = token._nguoiky
        self.output_folder  = token._output_folder

        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        self._target_position = 100
        self._current_position = 100
        self._enable = "on"
        # Reports if the cron is moving up or down.
        # >0 is up, <0 is down. This very much just for demonstration.
        self.moving = 0

        # Some static information about this device
        self.firmware_version = "0.0.1"
        self.model = "Tax Online token cron"

    @property
    def get_name(self) -> str:
        return self.name
    
    @property
    def get_serial_number(self) -> str:
        return self.serial_number
    
    @property
    def get_access_token(self) -> str:
        return self.access_token

    @property
    def get_pin(self) -> str:
        return self.pin

    @property
    def cron_id(self) -> str:
        """Return ID for cron."""
        return self._id

    @property
    def position(self):
        """Return position for cron."""
        return self._current_position

    async def set_position(self, position: int) -> None:
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        self._target_position = position

        # Update the moving status, and broadcast the update
        self.moving = position - 50
        await self.publish_updates()

        self._loop.create_task(self.delayed_update())

    async def running_cron(self) -> None:
        requestHeaders = {
            "Content-Type": "application/json",
        }

        
        requestBody = {
            "google_token": self.access_token,
            "tax_ids": self.tax_ids,
            "app": ["THUE"],
            "taikhoanTracuu" : self.taikhoanTracuu,
            "maDoiTuong"     : self.maDoiTuong,
            "nguoiky"        : self.nguoiky,
            "output_folder"  : self.output_folder,
            "serial_number"  : self.serial_number
        }

        requestURL = "http://" + self.token._api_ip_address + ":3000/api/convertExcelToXML"
        # future = self._loop.run_in_executor(None, requests.post, requestURL, data=json.dumps(requestBody), headers=requestHeaders)
        try:
            response = await self.token._hass.async_add_executor_job(lambda: requests.post(requestURL, data=json.dumps(requestBody), headers=requestHeaders))
            response = response.json()
        except:
            """"""
            response = {
                "status": 1,
                "message":"Could not connect to API or timeout"
            }

        if response:
            if "status" not in response or response["status"] != 0:
                _LOGGER.exception(response["message"])

    async def turn_on_cron(self) -> None:
        self._enable = "on"

    async def turn_off_cron(self) -> None:
        self._enable = "off"

    async def toggle_cron(self) -> None:
        if self._enable == "on":
            self._enable = "off"
        else:
            self._enable = "on"

    async def delayed_update(self) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        await asyncio.sleep(random.randint(1, 10))
        self.moving = 0
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when cron changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        self._current_position = self._target_position
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        """cron is online."""
        # The dummy cron is offline about 10% of the time. Returns True if online,
        # False if offline.
        return random.random() > 0.1

    @property
    def is_enable(self) -> bool:
        """Battery level as a percentage."""
        return self._enable

    @property
    def illuminance(self) -> int:
        """Return a sample illuminance in lux."""
        return random.randint(0, 500)
