"""Distance alert system for HC-SR04 + I2C LCD + buzzer + potentiometer threshold.

Improvements over earlier version:
 - Adds echo timeout protection so loop won't hang if sensor disconnects.
 - Takes multiple samples and averages for smoother readings.
 - Avoids clearing LCD every cycle (reduces flicker); only updates changed text.
 - Shows both measured distance and threshold on two lines.
 - Gracefully handles out-of-range readings (returns None).
 - Simple buzzer pulse option when inside threshold (easier to notice).
"""

import time
import machine
import utime
from machine import Pin, I2C

import lcd_api
import i2c_lcd

time.sleep(0.2)  # allow USB/serial to stabilize

# Pin setup (adjust if your wiring differs)
TRIG = machine.Pin(3, machine.Pin.OUT)
ECHO = machine.Pin(2, machine.Pin.IN)
BUZZ = machine.Pin(4, machine.Pin.OUT)
LED = machine.Pin("LED", machine.Pin.OUT)  # onboard LED indicator
pot = machine.ADC(26)  # threshold setting potentiometer

# LCD setup (I2C bus 0 on GP0=SDA, GP1=SCL)
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
lcd = i2c_lcd.I2cLcd(i2c, 0x27, 2, 16)  # change address if needed
try:
    lcd.set_backlight(True)
except Exception:
    pass  # some backpacks always have backlight on

SOUND_SPEED_CM_PER_US = 0.0343  # speed of sound (cm per microsecond)
MAX_ECHO_TIME_US = 30000  # (~5m max range) adjust for your sensor
SAMPLES = 3  # number of distance samples to average
BUZZER_PULSE_INTERVAL = 0.4  # seconds between buzzer pulses when active
_last_buzz_time = utime.ticks_ms()
BUZZ_ACTIVE_HIGH = True  # set to False if your buzzer is active-low
BUZZ_ON = 1 if BUZZ_ACTIVE_HIGH else 0
BUZZ_OFF = 0 if BUZZ_ACTIVE_HIGH else 1
LED.value(0)
BUZZ.value(BUZZ_OFF)

def _sanitize_unused_gpio():
    """Set all unused GPIOs to plain input (no pull) to avoid stray pulls/LEDs."""
    # GPIO used by this app: I2C(0,1), ECHO(2), TRIG(3), BUZZ(4), LED(25), BTN(20), POT ADC(26)
    used = {0, 1, 2, 3, 4, 25, 26}
    for p in range(29):  # 0..28 on Pico
        if p in used:
            continue
        try:
            machine.Pin(p, machine.Pin.IN)
        except Exception:
            pass

_sanitize_unused_gpio()

def _measure_single_echo_time():
    """Send a single trigger and measure echo time in microseconds.
    Returns echo flight time or None if timeout."""
    # Ensure trigger low
    TRIG.low()
    utime.sleep_us(2)
    # 10us trigger pulse
    TRIG.high()
    utime.sleep_us(10)
    TRIG.low()

    start_wait = utime.ticks_us()
    while ECHO.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start_wait) > MAX_ECHO_TIME_US:
            return None  # timeout waiting for echo rise
    signaloff = utime.ticks_us()

    while ECHO.value() == 1:
        if utime.ticks_diff(utime.ticks_us(), signaloff) > MAX_ECHO_TIME_US:
            return None  # timeout waiting for echo fall
    signalon = utime.ticks_us()

    return signalon - signaloff

def get_distance_cm():
    """Average several echo measurements, return distance in cm or None."""
    total = 0
    valid = 0
    for _ in range(SAMPLES):
        t = _measure_single_echo_time()
        if t is not None:
            total += t
            valid += 1
        utime.sleep_ms(5)
    if not valid:
        return None
    avg_time = total / valid
    distance = (avg_time * SOUND_SPEED_CM_PER_US) / 2
    # Basic sanity clamp
    if distance <= 0 or distance > 500:  # >5m treat as invalid for indoor use
        return None
    return distance

def cm_to_feet_inches(cm):
    if cm is None:
        return None, None
    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = int(round(total_inches - feet * 12))
    if inches == 12:
        feet += 1
        inches = 0
    return feet, inches

def cm_to_feet_whole(cm):
    """Convert centimeters to nearest whole feet (round) or None."""
    if cm is None:
        return None
    return int(round(cm / 30.48))

def read_threshold_cm():
    # Pot maps 0..65535 to 0..20 ft; convert to cm (1 ft = 30.48 cm)
    raw = pot.read_u16()
    feet = (raw / 65535) * 20.0
    return feet * 30.48

_last_line1 = ""
_last_line2 = ""

def _update_lcd(line1: str, line2: str):
    global _last_line1, _last_line2
    # Only redraw if content changed; clear once before redraw
    if line1 != _last_line1 or line2 != _last_line2:
        lcd.clear()
        lcd.putstr(line1[:16])
        lcd.putstr("\n")
        lcd.putstr(line2[:16])
        _last_line1, _last_line2 = line1, line2

def _buzz(active: bool):
    global _last_buzz_time
    if not active:
        BUZZ.value(BUZZ_OFF)
        return
    # Pulse buzzer periodically instead of continuous tone
    now = utime.ticks_ms()
    if utime.ticks_diff(now, _last_buzz_time) >= int(BUZZER_PULSE_INTERVAL * 1000):
        BUZZ.value(BUZZ_ON)
        utime.sleep_ms(100)
        BUZZ.value(BUZZ_OFF)
        _last_buzz_time = now

def main_loop():
    # Tolerance: +/- 6 inches
    tolerance_cm = 15.24  # 6 inches in cm
    global _last_line1, _last_line2
    # Start immediately in active mode
    LED.value(1)

    while True:
        dist_cm = get_distance_cm()
        # Live threshold from potentiometer (0..~20 ft mapped), used for alerting
        threshold_cm = read_threshold_cm()
        feet_whole = cm_to_feet_whole(dist_cm)
        thr_feet_whole = cm_to_feet_whole(threshold_cm)
        # Format lines
        if dist_cm is None:
            line1 = "Dist: -- ft"
        else:
            line1 = f"Dist: {feet_whole} ft"
        # Show target in whole feet
        line2 = f"Target:{thr_feet_whole} ft"
        _update_lcd(line1, line2)

        # Trigger only when whole feet match AND distance is within tolerance (6 inches)
        alert = (
            dist_cm is not None and
            feet_whole is not None and
            thr_feet_whole is not None and
            feet_whole == thr_feet_whole and
            abs(dist_cm - threshold_cm) <= tolerance_cm
        )
        _buzz(alert)
        utime.sleep_ms(60)

try:
    main_loop()
except KeyboardInterrupt:  # if run from a REPL
    BUZZ.value(BUZZ_OFF)
    LED.value(0)
    lcd.clear()
    lcd.putstr("Stopped")
except Exception as e:
    BUZZ.value(BUZZ_OFF)
    LED.value(0)
    lcd.clear()
    lcd.putstr("Error")
    try:
        print("Exception:", e)
    except Exception:
        pass