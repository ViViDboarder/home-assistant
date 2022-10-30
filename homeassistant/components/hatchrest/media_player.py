"""Hatchrest media player to control white noise."""
from __future__ import annotations

from pyhatchbabyrest.constants import PyHatchBabyRestSound

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_IDLE, STATE_OFF, STATE_PLAYING
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

    async_add_entities([HatchRestMediaPlayer(coordinator)], True)


class HatchRestMediaPlayer(HatchRestEntity, MediaPlayerEntity):
    """Control sound on Hatch Rest device."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    )

    _attr_sound_mode_list = [sound.name.capitalize() for sound in PyHatchBabyRestSound]
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _sound_mode_to_tone = {
        sound.name.capitalize(): sound for sound in PyHatchBabyRestSound
    }

    @property
    def name(self) -> str:
        """Hatch Rest sound name."""
        return f"{super().name} Sound"

    @property
    def sound_mode(self) -> str:
        """Hatch Rest white noise selection."""
        return self._device.sound.name.capitalize()

    @property
    def state(self) -> str:
        """State of hatch rest white noise."""
        if not self._device.power:
            return STATE_OFF

        if self._device.sound == PyHatchBabyRestSound.none:
            return STATE_IDLE

        return STATE_PLAYING

    @property
    def volume_level(self) -> float:
        """Volume level of Hatch Rest white noise."""
        return self._device.volume / 100

    async def async_turn_on(self):
        """Turn on the Hatch Rest sound. Allows specifying a tone and a volume."""
        if not self._device.power:
            await self._device.power_on()
            self._device.power = True

        self.async_write_ha_state()

    async def async_turn_off(self, **_):
        """Turn off the Hatch Rest sound. If the light is off, turn off the device."""
        if self.state == STATE_OFF:
            return

        # If light is on, only turn off sound otherwise power off
        if self._device.brightness:
            await self._device.set_sound(PyHatchBabyRestSound.none)
            self._device.sound = PyHatchBabyRestSound.none
        else:
            await self._device.power_off()
            self._device.power = False

        self.async_write_ha_state()

    async def async_select_sound_mode(self, sound_mode: str):
        """Switch the sound mode of the entity."""
        tone = self._sound_mode_to_tone[sound_mode]
        await self._device.set_sound(tone)
        self._device.sound = tone

        self.async_write_ha_state()

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        volume_percent = int(volume * 100)
        await self._device.set_volume(volume_percent)
        self._device.volume = volume_percent

        self.async_write_ha_state()
