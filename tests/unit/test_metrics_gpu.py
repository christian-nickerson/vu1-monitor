import GPUtil
import pytest
from pytest_mock import MockFixture

from vu1_monitor.metrics.gpu import get_gpu_utilisation


@pytest.fixture
def nvidia() -> GPUtil.GPU:
    return GPUtil.GPU(
        "test",
        "test",
        0.3,
        1,
        1,
        "test",
        "test",
        "test",
        "test",
        "test",
        "test",
        "test",
    )


def test_nvidia_utilisation(mocker: MockFixture, nvidia: GPUtil.GPU) -> None:
    """test nvidia gpu utilisation returns correctly"""
    mocker.patch.object(GPUtil, "getGPUs", return_value=[nvidia])
    response = get_gpu_utilisation("nvidia")
    assert response == nvidia.load * 100
