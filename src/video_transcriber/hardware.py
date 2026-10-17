import ctypes
import shutil
import sys
from typing import Tuple


def is_cuda_available() -> bool:
    try:
        if not shutil.which("nvidia-smi"):
            return False

        import ctranslate2
        if ctranslate2.get_cuda_device_count() <= 0:
            return False

        # On Windows, verify cublas runtime library is present and loadable
        if sys.platform == "win32":
            try:
                ctypes.cdll.LoadLibrary("cublas64_12.dll")
            except OSError:
                return False

        return True
    except Exception:
        return False

def determine_hardware(
    requested_device: str, 
    requested_compute_type: str
) -> Tuple[str, str]:
    """
    Returns (device, compute_type) based on request and availability.
    """
    device = requested_device.lower()
    compute_type = requested_compute_type.lower()
    
    if device == "auto":
        if is_cuda_available():
            device = "cuda"
        else:
            device = "cpu"
            
    if compute_type == "auto":
        if device == "cuda":
            compute_type = "float16"
        else:
            compute_type = "int8"
            
    return device, compute_type
