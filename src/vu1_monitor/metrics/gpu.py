import statistics

import GPUtil

from vu1_monitor.models.models import GPUBackend


def get_gpu_utilisation(backend: str | None = None) -> float:
    """Get GPU utilisation from device"""
    if backend:
        backend = GPUBackend(backend)

    if backend == GPUBackend.NVIDIA:
        return _get_nvidia_utilisation()
    elif backend == GPUBackend.AMD:
        return _get_amd_utilistion()
    else:
        return 0.0


def _get_nvidia_utilisation() -> float:
    """return NVIDA GPU utilisation (all devices)"""
    device_list = GPUtil.getGPUs()
    utilisation = [device.load * 100 for device in device_list]
    return statistics.fmean(utilisation)


def _get_amd_utilistion() -> float:
    """return AMD GPU utilisation (all devices). Loads library lazily to avoid device errors if not present."""
    from pyadl import ADLManager

    device_list = ADLManager.getInstance().getDevices()
    utilisation = [device.getCurrentUsage() for device in device_list]
    return statistics.fmean(utilisation)
