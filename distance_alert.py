import time
import machine
import utime
from machine import Pin, I2C

import lcd_api
import i2c_lcd

time.sleep(0.1)  # Wait for USB to become ready

# Pin setup
TRIG = machine.Pin(3, machine.Pin.OUT)
ECHO = machine.Pin(2, machine.Pin.IN)
BUZZ = machine.Pin(4, machine.Pin.OUT)
pot = machine.ADC(26)  # potentiometer for set distance (0–20 ft)

# LCD setup (I2C)
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
lcd = i2c_lcd.I2cLcd(i2c, 0x27, 2, 16)  # change 0x27 if your LCD uses a different address

def get_distance_cm():
    TRIG.low()
    utime.sleep_us(2)
    TRIG.high()
    utime.sleep_us(10)
    TRIG.low()

    # wait for echo start
    while ECHO.value() == 0:
        signaloff = utime.ticks_us()
    # wait for echo end
    while ECHO.value() == 1:
        signalon = utime.ticks_us()

    timepassed = signalon - signaloff
    return (timepassed * 0.0343) / 2  # cm

def cm_to_feet_inches(cm):
    if cm < 0:
        cm = 0
    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = int(round(total_inches - feet * 12))
    if inches == 12:
        feet += 1
        inches = 0
    return feet, inches

while True:
    # Distance measured
    distance_cm = get_distance_cm()
    feet, inches = cm_to_feet_inches(distance_cm)

    # Display distance on LCD
    lcd.clear()
    lcd.putstr(f"Distance: {feet}ft {inches}in")

    # Check if distance is below threshold
    threshold_cm = pot.read_u16() * (20 / 65535) * 30.48  # scale to 0–20 ft in cm
    if distance_cm < threshold_cm:
        BUZZ.high()
    else:
        BUZZ.low()

    time.sleep(0.1)