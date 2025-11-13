try:
    import machine  # MicroPython on device
except ImportError:
    from types import SimpleNamespace
    from typing import TYPE_CHECKING


    if TYPE_CHECKING:  # pragma: no cover - keep module type info for editors
        import machine as machine  # type: ignore  # noqa: F401
    else:
        # Desktop fallback so this file can run under CPython for quick tests
        class _HostPin:
            OUT = 1

            def __init__(self, pin_id, mode=None, value=0):
                self.pin_id = pin_id
                self.mode = mode
                self._value = value

            def value(self, level=None):
                if level is None:
                    return self._value
                self._value = 1 if level else 0
                print(f"[SIM] {self.pin_id} = {self._value}")

        machine = SimpleNamespace(Pin=_HostPin)  # type: ignore[assignment]

import sys
import time

"""Safe GPIO pulse tester.

Original list pulsed nearly every pin. This safer version excludes:
 - GP0, GP1 (I2C SDA/SCL) to avoid driving bus devices as push-pull.
 - GP2 (HC-SR04 Echo, sensor output pin) to avoid contention.
 - GP26 (ADC input / potentiometer) not an output.
You can re-add pins if you are certain they are safe outputs.
"""

# Safe test pins: selective outputs only (add/remove as needed)
TEST_PIN_IDS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 28, "LED"]
PULSE_DURATION = 0.2  # shorter pulse
PAUSE_BETWEEN_PINS = 0.15


def collect_pins():
    """Return (label, pin) tuples for every usable pin."""
    pins = []
    for identifier in TEST_PIN_IDS:
        label = f"GP{identifier}" if isinstance(identifier, int) else str(identifier)
        try:
            pin = machine.Pin(identifier, machine.Pin.OUT)
            pin.value(0)
        except Exception as exc:
            print(f"[WARN] Skipping {label}: {exc}")
            continue
        pins.append((label, pin))
    return pins


def pulse_pins_once(pin_table):
    """Send a single HIGH pulse to each pin, sequentially."""
    print("Beginning safe single-pass GPIO test...")
    for label, pin in pin_table:
        print(f"Pulsing {label}")
        pin.value(1)
        time.sleep(PULSE_DURATION)
        pin.value(0)
        time.sleep(PAUSE_BETWEEN_PINS)
    print("Done. Safe GPIO pins pulsed once.")


def main():
    pins = collect_pins()
    if not pins:
        print("No GPIO pins available. Check your board configuration.")
        return
    try:
        pulse_pins_once(pins)
    except Exception as exc:
        print("Error during GPIO test:", exc)
        try:
            sys.print_exception(exc)
        except Exception:
            pass


if __name__ == "__main__":
    print("main.py starting � single-pass GPIO test")
    main()
