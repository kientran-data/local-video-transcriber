import shutil
from typing import Tuple


def is_cuda_available() -> bool:
    try:
        # Check if nvidia-smi exists as a quick heuristic
        if shutil.which("nvidia-smi"):
            import torch
            return torch.cuda.is_available()
    except ImportError:
        pass
        
    # Try ctranslate2 if torch isn't installed
    try:
        import ctranslate2
        return ctranslate2.get_cuda_device_count() > 0
    except ImportError:
        pass
    except Exception:
        pass
        
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
