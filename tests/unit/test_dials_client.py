import json
from pathlib import Path

import pytest
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from vu1_monitor.dials.client import VU1Client
from vu1_monitor.dials.models import Dial, DialType
from vu1_monitor.exceptions.dials import (
    DialNotFound,
    DialNotImplemented,
    ServerNotFound,
)


@pytest.fixture
def dial_body() -> dict:
    with open(Path("tests/fixtures/dials.json")) as f:
        return json.load(f)


@pytest.fixture
def value_body() -> dict:
    with open(Path("tests/fixtures/values.json")) as f:
        return json.load(f)


@pytest.fixture
def backlight_body() -> dict:
    with open(Path("tests/fixtures/backlight.json")) as f:
        return json.load(f)


@pytest.fixture
def image_body() -> dict:
    with open(Path("tests/fixtures/image.json")) as f:
        return json.load(f)


@pytest.fixture
def image_file() -> Path:
    return Path("tests/fixtures/blank.png")


@pytest.fixture
def client() -> VU1Client:
    return VU1Client("test", 5430, "test", testing=True)


@pytest.fixture
def client_loaded(httpx_mock: HTTPXMock, dial_body: dict) -> VU1Client:
    httpx_mock.add_response(json=dial_body)
    return VU1Client("test", 5430, "test")


#############################
### Get / Load Dial tests ###
#############################


def test_get_dials(httpx_mock: HTTPXMock, client: VU1Client, dial_body: dict):
    """test get dials manipulates body correctly"""
    httpx_mock.add_response(json=dial_body)
    response = client.get_dials()
    assert response == dial_body["data"]


def test_get_dials_raises(httpx_mock: HTTPXMock, client: VU1Client, dial_body: dict):
    """test get dials raises HTTPError on non 200"""
    httpx_mock.add_response(status_code=400, json=dial_body)
    with pytest.raises(HTTPError):
        client.get_dials()


def test_load_dials(httpx_mock: HTTPXMock, client: VU1Client, dial_body: dict):
    """test load dials populates dials correctly"""
    httpx_mock.add_response(json=dial_body)
    client._load_dials()
    assert len(client.dials) == len(dial_body["data"])
    for dial in client.dials:
        assert isinstance(client.dials[dial], Dial)


def test_load_dials_server_off(httpx_mock: HTTPXMock, client: VU1Client, dial_body: dict):
    """test load dials fails correctly when server not online"""
    httpx_mock.add_response(status_code=500, json=dial_body)
    with pytest.raises(ServerNotFound):
        client._load_dials()


def test_load_dials_no_dials_configured(httpx_mock: HTTPXMock, client: VU1Client, dial_body: dict):
    """test load dials fails when no dials have been configured"""
    dial_body["data"] = []
    httpx_mock.add_response(json=dial_body)
    with pytest.raises(DialNotFound, match="no dials returned from VU Server"):
        client._load_dials()


def test_load_dials_no_dials_correctly_configured(httpx_mock: HTTPXMock, client: VU1Client, dial_body: dict):
    """test load dials fails when no dials have been configured correctly (mismatch names)"""
    new_dials = []
    for dial in dial_body["data"]:
        dial["dial_name"] = "test"
        new_dials.append(dial)
    dial_body["data"] = new_dials

    httpx_mock.add_response(json=dial_body)
    with pytest.raises(DialNotFound, match="no known dials found"):
        client._load_dials()


######################
### Set Dial tests ###
######################


def test_set_dial(httpx_mock: HTTPXMock, client_loaded: VU1Client, value_body: dict):
    """test set_dial returns correctly"""
    httpx_mock.add_response(json=value_body)
    response = client_loaded.set_dial(DialType.CPU, 50)
    assert response == value_body


def test_set_dial_no_dials(
    httpx_mock: HTTPXMock,
    client_loaded: VU1Client,
    value_body: dict,
    assert_all_responses_were_requested: bool,
):
    """test set_dial raises when dial selected not found at load"""
    httpx_mock.add_response(json=value_body)
    client_loaded.dials.pop(DialType.CPU.value, None)
    with pytest.raises(DialNotImplemented):
        client_loaded.set_dial(DialType.CPU, 50)


def test_set_dial_non_200(httpx_mock: HTTPXMock, client_loaded: VU1Client, value_body: dict):
    """test set_dial call fails correctly"""
    httpx_mock.add_response(status_code=400, json=value_body)
    with pytest.raises(HTTPError):
        client_loaded.set_dial(DialType.CPU, 50)


def test_set_dial_500(httpx_mock: HTTPXMock, client_loaded: VU1Client, value_body: dict):
    """test set_dial call raises ServerNotFound on 500"""
    httpx_mock.add_response(status_code=500, json=value_body)
    with pytest.raises(ServerNotFound):
        client_loaded.set_dial(DialType.CPU, 50)


###########################
### Set Backlight tests ###
###########################


def test_set_backlight(httpx_mock: HTTPXMock, client_loaded: VU1Client, backlight_body: dict):
    """test set_backlight returns correctly"""
    httpx_mock.add_response(json=backlight_body)
    response = client_loaded.set_backlight(DialType.CPU, (50, 50, 50))
    assert response == backlight_body


def test_set_backlight_no_dials(
    httpx_mock: HTTPXMock,
    client_loaded: VU1Client,
    backlight_body: dict,
    assert_all_responses_were_requested: bool,
):
    """test set_backlight raises when dial selected not found at load"""
    httpx_mock.add_response(json=backlight_body)
    client_loaded.dials.pop(DialType.CPU.value, None)
    with pytest.raises(DialNotImplemented):
        client_loaded.set_backlight(DialType.CPU, (50, 50, 50))


def test_set_backlight_non_200(httpx_mock: HTTPXMock, client_loaded: VU1Client, backlight_body: dict):
    """test set_backlight call raises HTTPError on non-200"""
    httpx_mock.add_response(status_code=400, json=backlight_body)
    with pytest.raises(HTTPError):
        client_loaded.set_backlight(DialType.CPU, (50, 50, 50))


def test_set_backlight_500(httpx_mock: HTTPXMock, client_loaded: VU1Client, backlight_body: dict):
    """test set_backlight call raises ServerNotFound on 500"""
    httpx_mock.add_response(status_code=500, json=backlight_body)
    with pytest.raises(ServerNotFound):
        client_loaded.set_backlight(DialType.CPU, (50, 50, 50))


#######################
### Set Image tests ###
#######################


def test_set_image(httpx_mock: HTTPXMock, client_loaded: VU1Client, image_body: dict, image_file: Path):
    """test set_image returns correctly"""
    httpx_mock.add_response(json=image_body)
    response = client_loaded.set_image(DialType.CPU, image_file)
    assert response == image_body


def test_set_image_no_dials(
    httpx_mock: HTTPXMock,
    client_loaded: VU1Client,
    image_body: dict,
    image_file: Path,
    assert_all_responses_were_requested: bool,
):
    """test set_image raises when dial selected not found at load"""
    httpx_mock.add_response(json=image_body)
    client_loaded.dials.pop(DialType.CPU.value, None)
    with pytest.raises(DialNotImplemented):
        client_loaded.set_image(DialType.CPU, image_file)


def test_set_image_non_200(httpx_mock: HTTPXMock, client_loaded: VU1Client, image_body: dict, image_file: Path):
    """test set_image call raises HTTPError on non-200"""
    httpx_mock.add_response(status_code=400, json=image_body)
    with pytest.raises(HTTPError):
        client_loaded.set_image(DialType.CPU, image_file)


def test_set_image_500(httpx_mock: HTTPXMock, client_loaded: VU1Client, image_body: dict, image_file: Path):
    """test set_image call raises ServerNotFound on 500"""
    httpx_mock.add_response(status_code=500, json=image_body)
    with pytest.raises(ServerNotFound):
        client_loaded.set_image(DialType.CPU, image_file)
