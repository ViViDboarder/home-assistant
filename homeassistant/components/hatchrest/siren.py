"""Siren platform for Hatch Rest."""
from __future__ import annotations

from pyhatchbabyrest.constants import PyHatchBabyRestSound

from homeassistant.components.siren import SirenEntity, SirenEntityFeature
from homeassistant.components.siren.const import ATTR_TONE, ATTR_VOLUME_LEVEL
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HatchRestEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hatch Rest sound controls."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([HatchRestSiren(coordinator)], True)


class HatchRestSiren(HatchRestEntity, SirenEntity):
    """Hatch Rest sound controls."""

    @property
    def name(self) -> str:
        """Name of Hatch Rest sound entity."""
        return f"{super().name} Sound"

    @property
    def supported_features(self) -> int:
        """List supported features."""
        return (
            SirenEntityFeature.TONES
            | SirenEntityFeature.VOLUME_SET
            | SirenEntityFeature.TURN_ON
            | SirenEntityFeature.TURN_OFF
        )

    @property
    def available_tones(self) -> dict[int, str]:
        """Return available sound mapping enum val to string."""
        return {sound.value: sound.name for sound in PyHatchBabyRestSound}

    @property
    def tone(self) -> int:
        """Return current sound enum value."""
        return self._device.sound

    @property
    def is_on(self) -> bool:
        """Return current sound status."""
        return self._device.power and self.tone != PyHatchBabyRestSound.none

    async def async_turn_on(self, **kwargs):
        """Turn on the Hatch Rest sound. Allows specifying a tone and a volume."""
        if not self._device.power:
            await self._device.power_on()
            self._device.power = True

        tone = kwargs.get(ATTR_TONE)
        if tone:
            await self._device.set_sound(tone)
            self._device.sound = tone

        volume = kwargs.get(ATTR_VOLUME_LEVEL)
        if volume is not None:
            await self._device.set_volume(int(volume * 100))
            self._device.volume = int(volume * 100)

        self.async_write_ha_state()

    async def async_turn_off(self, **_):
        """Turn off the Hatch Rest sound. If the light is off, turn off the device."""
        if not self.is_on:
            return

        # If light is on, only turn off sound otherwise power off
        if self._device.brightness:
            await self._device.set_sound(PyHatchBabyRestSound.none)
            self._device.sound = PyHatchBabyRestSound.none
        else:
            await self._device.power_off()
            self._device.power = False

        self.async_write_ha_state()
