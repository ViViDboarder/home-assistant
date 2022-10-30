"""Tests for the hatchrest light."""

from unittest.mock import MagicMock

from pyhatchbabyrest import PyHatchBabyRestAsync
import pytest

from homeassistant.components.hatchrest import HatchRestCoordinator
from homeassistant.components.hatchrest.light import HatchRestLight
from homeassistant.core import HomeAssistant

from . import VALID_HATCHREST_ENTRY


@pytest.fixture
def _mock_client():
    client = MagicMock(spec=PyHatchBabyRestAsync)
    client.name = "Hatch Baby Rest"
    client.power = False
    client.brightness = 0
    client.color = (0, 0, 0)
    return client


@pytest.fixture
def _mock_entry(hass: HomeAssistant):
    entry = VALID_HATCHREST_ENTRY
    entry.add_to_hass(hass)
    return entry


async def test_light(
    hass: HomeAssistant,
    _mock_client: PyHatchBabyRestAsync,
):
    """Test light component coordination for Hatch Rest."""
    coordinator = HatchRestCoordinator(hass, None, _mock_client)
    light = HatchRestLight(coordinator)
    light.hass = MagicMock(spec=HomeAssistant)
    light.entity_id = "light.hatch_baby_rest"

    assert light.name == "Hatch Baby Rest Light"
    assert not light.is_on

    await light.async_turn_on(brightness=100)
    assert coordinator.device.power_on.called_once()
    assert coordinator.device.set_brightness.called_once_with(100)

    assert light.is_on
    assert light.brightness == 100
