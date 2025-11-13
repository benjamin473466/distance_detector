from machine import I2C
from lcd_api import LcdApi
import utime

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 0x08
        self._init_lcd()
        super().__init__()

    def set_backlight(self, on: bool) -> None:
        """Turn the LCD backlight on or off (if supported by backpack)."""
        self.backlight = 0x08 if on else 0x00

    def _init_lcd(self):
        utime.sleep_ms(20)
        self._write_byte(0x30)
        utime.sleep_ms(5)
        self._write_byte(0x30)
        utime.sleep_ms(1)
        self._write_byte(0x30)
        self._write_byte(0x20)
        self.hal_write_command(self.LCD_FUNCTION | self.LCD_FUNCTION_2LINES)
        self.hal_write_command(self.LCD_DISPLAY_CTRL | self.LCD_DISPLAY_ON)
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_LEFT)

    def hal_write_command(self, cmd):
        self._write4bits(cmd, 0)

    def hal_write_data(self, data):
        self._write4bits(data, 1)

    def hal_sleep_ms(self, ms):
        utime.sleep_ms(ms)

    def _write4bits(self, data, mode):
        high = data & 0xF0
        low = (data << 4) & 0xF0
        self._write_byte(high | mode)
        self._write_byte(low | mode)

    def _write_byte(self, data):
        self.i2c.writeto(self.i2c_addr, bytes([data | self.backlight]))
        self._pulse_enable(data)

    def _pulse_enable(self, data):
        self.i2c.writeto(self.i2c_addr, bytes([data | 0x04 | self.backlight]))
        utime.sleep_us(500)
        self.i2c.writeto(self.i2c_addr, bytes([(data & ~0x04) | self.backlight]))
        utime.sleep_us(100)