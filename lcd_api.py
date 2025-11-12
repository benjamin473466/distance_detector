class LcdApi:
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_CTRL = 0x08
    LCD_SHIFT = 0x10
    LCD_FUNCTION = 0x20
    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80

    LCD_ENTRY_SHIFT_INC = 0x01
    LCD_ENTRY_LEFT = 0x02

    LCD_DISPLAY_ON = 0x04
    LCD_CURSOR_ON = 0x02
    LCD_BLINK_ON = 0x01

    LCD_FUNCTION_8BIT = 0x10
    LCD_FUNCTION_2LINES = 0x08
    LCD_FUNCTION_5x10DOTS = 0x04

    def __init__(self):
        self.num_lines = 2
        self.num_columns = 16

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        self.hal_sleep_ms(2)

    def putstr(self, string):
        for char in string:
            if char == '\n':
                self.next_line()
            else:
                self.hal_write_data(ord(char))

    def next_line(self):
        self.hal_write_command(0xC0)  # move to 2nd line

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError

    def hal_sleep_ms(self, ms):
        raise NotImplementedError