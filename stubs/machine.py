# Stub for the MicroPython 'machine' module
class Pin:
    OUT = 0
    IN = 1

    def __init__(self, pin_id, mode=None):
        pass

    def value(self, val=None):
        pass

class I2C:
    def __init__(self, id, sda, scl):
        pass

    def writeto(self, addr, buf):
        pass

class ADC:
    def __init__(self, pin):
        pass

    def read_u16(self):
        return 0