from pathlib import Path

import httpx
import pytest
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from vu1_monitor.dials.client import VU1Client, server_handler
from vu1_monitor.exceptions.dials import (
    DialNotFound,
    DialNotImplemented,
    ServerNotFound,
)
from vu1_monitor.models.models import Dial, DialType


@pytest.fixture
def client() -> VU1Client:
    return VU1Client("test", 5430, "test", testing=True)


@pytest.fixture
def client_loaded(httpx_mock: HTTPXMock, dial_body: dict) -> VU1Client:
    httpx_mock.add_response(json=dial_body)
    return VU1Client("test", 5430, "test")


##################################
### Server Conn Error Handling ###
##################################


def test_server_conn_error(httpx_mock: HTTPXMock) -> None:
    """test server_conn handles connection errors correctly"""
    httpx_mock.add_exception(httpx.ConnectError("test"))
    httpx_mock.add_response()

    @server_handler()
    def request_test():
        with httpx.Client() as client:
            return client.get("http://test")

    with pytest.raises(ServerNotFound):
        request_test()


def test_server_timeout_error(httpx_mock: HTTPXMock) -> None:
    """test server_conn handles timeout errors correctly"""
    for _ in range(2):
        httpx_mock.add_exception(httpx.TimeoutException("test"))
    httpx_mock.add_response(status_code=200)

    @server_handler(2)
    def request_test():
        with httpx.Client() as client:
            return client.get("http://test")

    response = request_test()
    assert response.status_code == 200


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


def test_check_dial_exists(httpx_mock: HTTPXMock, client_loaded: VU1Client):
    """test check_dial returns true"""
    assert client_loaded.check_dial(DialType.CPU) is True


def test_check_dial_not_exists(httpx_mock: HTTPXMock, client_loaded: VU1Client):
    """test check_dial returns false"""
    client_loaded.dials.pop(DialType.CPU.value, None)
    assert client_loaded.check_dial(DialType.CPU) is False


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
