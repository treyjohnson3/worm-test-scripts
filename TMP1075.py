import smbus2

## I think I wrote everything correctly, so it should work, but this is all untested ####

# Datasheet shows 16bit config register, but it is compatible with singly byte read/write operations
REGISTER_TEMPERATURE = 0b00000000
REGISTER_CONFIGURATION = 0b00000001

CONFIG_CONVERSION_RATE_MASK = 0b01100000
CONFIG_FAULT_MASK = 0b00011000
CONFIG_SHUTDOWN_MASK = 0b00000001

# need to finish adding other config settings, and possibly all fo the alert stuff if we are using it

CONFIG_CONVERSION_RATE_27ms = 0b0000000000
CONFIG_CONVERSION_RATE_55ms = 0b0010000000
CONFIG_CONVERSION_RATE_110ms = 0b0100000000

CONFIG_SHUTDOWN_CONTINUOUS = 0b00000000
CONFIG_SHUTDOWN_SINGLE = 0b00000001

CONFIG_ONESHOT = 0b10000000


############## this sensor has high and low alert functions, are we going to use them? ##############
class TempSensor:
    def __init__(self, address):
        self.bus = smbus2.SMBus(1)
        self.addr = address
        self.shutdown = CONFIG_SHUTDOWN_SINGLE
        self.conversion_rate = CONFIG_CONVERSION_RATE_110ms
        self.temp = 0
        self.current_config = 0b00000000

    def set_shutdown(self, shutdown):
        self.shutdown = shutdown
        self.write_to_config(shutdown, CONFIG_SHUTDOWN_MASK)

    def set_conversion_rate(self, rate):
        self.conversion_rate = rate
        self.write_to_config(rate, CONFIG_CONVERSION_RATE_MASK)

    def write_to_config(self, new_config, mask):
        config_message = (self.current_config & ~mask) | new_config
        self.i2c.write_byte_data(
            self.addr, REGISTER_CONFIGURATION, config_message)
        self.current_config == config_message

    def read_temp(self):
        if self.shutdown == CONFIG_SHUTDOWN_SINGLE:
            self.i2c.write_byte_data(
                self.addr, REGISTER_CONFIGURATION, CONFIG_ONESHOT)
        data = self.i2c.read_i2c_block_data(
            self.address, REGISTER_TEMPERATURE, 2)
        self.temp = data
        return data

    def read_temp_celcius(self):
        return self.convert_to_celcius(self.read_temp())

    def convert_to_celcius(self, data):
        # shift out last 4 bits (sensor returns a 12bit value)
        data = data >> 4
        if data >= 2048:  # twos complement -- this is true if data value is negative
            return -(data-2048)/16
        else:
            return data/16

    def close(self):
        self.bus.close()
