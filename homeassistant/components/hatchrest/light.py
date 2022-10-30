"""Light platform for Hatch Rest."""
from __future__ import annotations

from pyhatchbabyrest.pyhatchbabyrest import PyHatchBabyRestSound

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
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
    """Set up Hatch Rest light controls."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([HatchRestLight(coordinator)], True)


class HatchRestLight(HatchRestEntity, LightEntity):
    """Control of the lighting features of the Hatch Rest."""

    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}

    @property
    def name(self) -> str:
        """Hatch Rest light name."""
        return f"{super().name} Light"

    @property
    def is_on(self) -> bool:
        """Light state of the Hatch Rest device."""
        return self._device.power and self.brightness > 0

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Color state of the Hatch Rest light."""
        return self._device.color

    @property
    def brightness(self) -> int:
        """Brightness of the Hatch Rest light."""
        return self._device.brightness

    async def async_turn_on(self, **kwargs):
        """Turn on the Hatch Rest light and set color and brightness."""
        if not self._device.power:
            await self._device.power_on()
            self._device.power = True

        color = kwargs.get(ATTR_RGB_COLOR)
        if color:
            await self._device.set_color(*color)
            self._device.color = color

        brightness = kwargs.get(ATTR_BRIGHTNESS)
        # When turning on, always set some minimum level of brightness
        brightness = brightness or 1
        await self._device.set_brightness(brightness)
        self._device.brightness = brightness

        self.async_write_ha_state()

    async def async_turn_off(self, **_):
        """Turn off the Hatch Rest light. If the sound is off, turn off the device."""
        if not self.is_on:
            return

        # If sound is on, only turn off the light
        if self._device.sound != PyHatchBabyRestSound.none:
            await self._device.set_brightness(0)
            self._device.brightness = 0
        else:
            await self._device.power_off()
            self._device.power = False

        self.async_write_ha_state()
