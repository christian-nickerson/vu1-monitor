import GPUtil
from pyadl import ADLManager

from vu1_monitor.models.models import GPUBackend


def get_gpu_utilisation(backend: str | None = None) -> float:
    """Get GPU utilisation from device"""
    if not backend:
        backend = GPUBackend(backend)

    if len(GPUtil.getGPUs()) > 0 or backend == GPUBackend.NVIDIA:
        return GPUtil.getGPUs()[0].load * 100
    elif len(ADLManager.getInstance().getDevices()) > 0 or backend == GPUBackend.AMD:
        return ADLManager.getInstance().getDevices()[0].getCurrentUsage()
    else:
        return 0.0
