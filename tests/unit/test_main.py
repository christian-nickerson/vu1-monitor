from itertools import product

import pytest
from click.testing import CliRunner
from pytest_mock import MockFixture

from vu1_monitor.dials.client import VU1Client
from vu1_monitor.dials.models import Bright, Colours, DialType
from vu1_monitor.main import backlight, image


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_backlight_all(mocker: MockFixture, runner: CliRunner, dial_body: dict):
    """Test backlight returns successfully for all dials"""
    mocker.patch.object(VU1Client, "get_dials", return_value=dial_body["data"])
    mocker.patch.object(VU1Client, "set_backlight")

    result = runner.invoke(backlight)
    assert result.exit_code == 0


def test_backlight_args(mocker: MockFixture, runner: CliRunner, dial_body: dict):
    """Test backlight returns successfully with specific args"""
    mocker.patch.object(VU1Client, "get_dials", return_value=dial_body["data"])
    mocker.patch.object(VU1Client, "set_backlight")

    for dial, colour, brighness in product(DialType, Colours, Bright):
        result = runner.invoke(
            backlight,
            ["--dial", dial.value, "--colour", colour.name, "--brightness", brighness.name],
        )
        assert result.exit_code == 0


def test_backlight_invalid_args(mocker: MockFixture, runner: CliRunner, dial_body: dict):
    """Test backlight fails with incorrect args"""
    mocker.patch.object(VU1Client, "get_dials", return_value=dial_body["data"])
    mocker.patch.object(VU1Client, "set_backlight")

    result = runner.invoke(backlight, ["--dial", "CPU (Hub)"])
    assert result.exit_code > 0

    result = runner.invoke(backlight, ["--colour", "BLACK"])
    assert result.exit_code > 0

    result = runner.invoke(backlight, ["--brightness", "a bit"])
    assert result.exit_code > 0


def test_image(mocker: MockFixture, runner: CliRunner, dial_body: dict):
    """Test image returns successfully"""
    mocker.patch.object(VU1Client, "get_dials", return_value=dial_body["data"])
    mocker.patch.object(VU1Client, "set_image")

    result = runner.invoke(image, ["tests/fixtures/blank.png", "--dial", "CPU"])
    assert result.exit_code == 0


def test_image_bad_image(mocker: MockFixture, runner: CliRunner, dial_body: dict):
    """Test image fails with bad image args / files"""
    mocker.patch.object(VU1Client, "get_dials", return_value=dial_body["data"])
    mocker.patch.object(VU1Client, "set_image")

    result = runner.invoke(image, ["tests/fixtures/blank-bad.png", "--dial", "CPU"])
    assert result.exit_code > 0

    result = runner.invoke(image, ["tests/fixtures/image.json", "--dial", "CPU"])
    assert result.exit_code > 0

    result = runner.invoke(image, ["tests/fixtures/test.txt", "--dial", "CPU"])
    assert result.exit_code > 0

    result = runner.invoke(image, ["tests/fixtures/blank.png", "--dial", "CPU (Hub)"])
    assert result.exit_code > 0
