"""Local Video Transcriber."""

import os
import sys

# Configure Windows console encoding and CUDA DLL search path
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    for cuda_dir in [r"D:\cuda-bin", r"C:\cuda-bin"]:
        if os.path.isdir(cuda_dir):
            if cuda_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = cuda_dir + ";" + os.environ.get("PATH", "")
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(cuda_dir)
                except Exception:
                    pass

# PyAV compatibility shim for av >= 15
try:
    import av
    _orig_av_open = av.open

    def _safe_av_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(*args, **kwargs)

    av.open = _safe_av_open
except (ImportError, AttributeError):
    pass
