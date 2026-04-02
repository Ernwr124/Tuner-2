import platform
import psutil
import subprocess
import json
import os
import sys

def get_cuda_info():
    """Detect NVIDIA GPU and VRAM."""
    try:
        # Get GPU Name
        name_output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            encoding='utf-8'
        ).strip()

        # Get VRAM in MiB
        vram_output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            encoding='utf-8'
        ).strip()

        return {
            "gpu": name_output,
            "vram_gb": round(float(vram_output) / 1024, 2),
            "backend": "unsloth"
        }
    except Exception:
        return None

def get_apple_silicon_info():
    """Detect Apple Silicon (M-series)."""
    if platform.system() == "Darwin":
        try:
            brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], encoding='utf-8')
            if "Apple" in brand:
                mem_output = subprocess.check_output(["sysctl", "-n", "hw.memsize"], encoding='utf-8').strip()
                return {
                    "chip": brand.strip(),
                    "unified_memory_gb": round(int(mem_output) / (1024**3), 2),
                    "backend": "mlx"
                }
        except Exception:
            pass
    return None

def scout_hardware():
    """Main function to gather system information."""
    info = {
        "os": platform.system(),
        "os_release": platform.release(),
        "cpu": {
            "count": psutil.cpu_count(logical=True),
            "physical_count": psutil.cpu_count(logical=False),
        },
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "cuda": get_cuda_info(),
        "apple_silicon": get_apple_silicon_info()
    }

    if info["cuda"]:
        info["preferred_engine"] = "unsloth"
    elif info["apple_silicon"]:
        info["preferred_engine"] = "mlx"
    else:
        info["preferred_engine"] = "cpu"

    return info
