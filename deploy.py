"""
Deploy helper for Raspberry Pi Pico (MicroPython) using mpremote.

Features:
- Upload required files (distance_alert.py, i2c_lcd.py, lcd_api.py)
- Optionally copy as main.py for auto-run on boot
- Optionally run the script after upload
- Works whether mpremote is installed as a command or as a Python module

Usage examples (Windows PowerShell):
  python deploy.py --run
  python deploy.py --as-main
  python deploy.py --as-main --run

Notes:
- Ensure the Pico is connected and enumerated; mpremote will auto-select.
- If you get connection issues, try: mpremote connect auto reset
"""

import shutil
import subprocess
import sys
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).parent
REQUIRED_FILES = [
    PROJECT_ROOT / "distance_alert.py",
    PROJECT_ROOT / "i2c_lcd.py",
    PROJECT_ROOT / "lcd_api.py",
]


def mpremote_base() -> list[str]:
    """Return the base command to invoke mpremote.
    Prefer 'mpremote' if available; otherwise use 'python -m mpremote'."""
    # Try direct 'mpremote'
    try:
        subprocess.run(["mpremote", "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return ["mpremote"]
    except Exception:
        # Fallback to python -m mpremote
        return [sys.executable, "-m", "mpremote"]


def run_cmd(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd)
    return proc.returncode


def cp_file(src: Path, dest_name: str) -> int:
    base = mpremote_base()
    cmd = base + ["cp", str(src), f":{dest_name}"]
    return run_cmd(cmd)


def run_file(filename_on_device: str) -> int:
    base = mpremote_base()
    # mpremote run takes a local file; we can pass our project file path.
    # If the file is already on the device as main.py, simply soft reset then return.
    local_path = PROJECT_ROOT / filename_on_device
    if local_path.exists():
        cmd = base + ["run", str(local_path)]
        return run_cmd(cmd)
    else:
        # If local file doesn't exist (e.g., running main.py), just open REPL and reset
        cmd = base + ["connect", "auto", "reset"]
        return run_cmd(cmd)


def ensure_files_exist() -> None:
    missing = [p for p in REQUIRED_FILES if not p.exists()]
    if missing:
        names = ", ".join(str(p.name) for p in missing)
        raise SystemExit(f"Missing required files: {names}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deploy Pico files via mpremote")
    parser.add_argument("--as-main", action="store_true", help="Copy distance_alert.py as main.py on the device")
    parser.add_argument("--run", action="store_true", help="Run the script after upload")
    args = parser.parse_args(argv)

    ensure_files_exist()

    # Upload dependencies first
    for p in REQUIRED_FILES:
        rc = cp_file(p, p.name)
        if rc != 0:
            return rc

    # Optionally set as main.py
    if args.as_main:
        rc = cp_file(PROJECT_ROOT / "distance_alert.py", "main.py")
        if rc != 0:
            return rc
        target = "main.py"
    else:
        target = "distance_alert.py"

    # Optionally run
    if args.run:
        return run_file(target)

    print("Deploy complete.")
    if args.as_main:
        print("distance_alert.py copied as main.py; will auto-run on boot.")
    else:
        print("Use --run to execute now, or rename to main.py for auto-run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
