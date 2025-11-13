import machine
from machine import Pin, I2C
import utime

# Use I2C(0) on GP0=SDA, GP1=SCL to match your wiring
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
print("Scanning I2C bus 0 (GP0 SDA, GP1 SCL)...")
utime.sleep_ms(100)
devices = i2c.scan()
if devices:
    print("Found devices:")
    for d in devices:
        print(" - 0x%02X" % d)
else:
    print("No I2C devices found. Check wiring, power, and contrast knob.")
