"""Record a reproducibility snapshot of the compute environment.

Run inside the project venv on the DGX. Writes JSON to docs/env_snapshot.json.
"""
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone


def run(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def main():
    snapshot = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "cuda_visible_devices": run("echo $CUDA_VISIBLE_DEVICES"),
        "nvidia_smi_L": run("nvidia-smi -L"),
        "git_commit": run("git -C ~/Vishresearch/AIHUMAN rev-parse HEAD"),
        "git_status": run("git -C ~/Vishresearch/AIHUMAN status --short"),
        "pip_freeze": run("pip freeze"),
    }

    try:
        import torch

        snapshot["torch_version"] = torch.__version__
        snapshot["torch_cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            snapshot["torch_device_name"] = torch.cuda.get_device_name(0)
            snapshot["torch_device_mem_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
    except ImportError:
        snapshot["torch_version"] = None

    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
