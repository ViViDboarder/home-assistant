"""Select platform for Hatch Rest."""
from __future__ import annotations

from pyhatchbabyrest.constants import PyHatchBabyRestSound

from homeassistant.components.select import SelectEntity
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
    """Set up Hatch Rest sound."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([HatchRestSelect(coordinator)], True)


class HatchRestSelect(HatchRestEntity, SelectEntity):
    """Select options for noise to be played by the Hatch Rest."""

    @property
    def name(self) -> str:
        """Name of the Hatch Rest sound select entity."""
        return f"{super().name} Sound Select"

    @property
    def options(self) -> list[str]:
        """Possible sound options as strings."""
        return [sound.name.capitalize() for sound in PyHatchBabyRestSound]

    @property
    def current_option(self) -> str:
        """Return currently selected sound option as a string."""
        return {sound.value: sound.name.capitalize() for sound in PyHatchBabyRestSound}[
            self._device.sound
        ]

    async def async_select_option(self, option: str):
        """Select sound option using string name."""
        tone = {sound.name.lower(): sound for sound in PyHatchBabyRestSound}[
            option.lower()
        ]
        await self._device.set_sound(tone)
        self._device.sound = tone

        self.async_write_ha_state()
