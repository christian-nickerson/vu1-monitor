import json
from pathlib import Path

import pytest
from dynaconf import settings  # type: ignore


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


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
