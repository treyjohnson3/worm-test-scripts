import smbus2
import struct
import time
import math

#####################################
# may need to adjust for circuit python so it can run on seesaw (use busio insead of smbus2)
# code only applicable for ADS 1219
###################################


_CHANNEL_MASK = 0b11100000
_GAIN_MASK = 0b000100000
_DR_MASK = 0b00001100
_CM_MASK = 0b00000010
_VREF_MASK = 0b00000001

_COMMAND_RESET = 0b00000110
_COMMAND_START_SYNC = 0b00001000
_COMMAND_POWERDOWN = 0b00000010
_COMMAND_RDATA = 0b00010000
_COMMAND_RREG_CONFIG = 0b00100000
_COMMAND_RREG_STATUS = 0b00100100
_COMMAND_WREG_CONFIG = 0b01000000

_DRDY_MASK = 0b10000000\
    # need this only if implementing read_status function
_DRDY_NO_NEW_RESULT = 0b00000000   # No new conversion result available
_DRDY_NEW_RESULT_READY = 0b10000000  # New conversion result ready

CHANNEL_AIN0_AIN1 = 0b00000000  # Differential P = AIN0, N = AIN1 (default)
CHANNEL_AIN2_AIN3 = 0b00100000  # Differential P = AIN2, N = AIN3
CHANNEL_AIN1_AIN2 = 0b01000000  # Differential P = AIN1, N = AIN
CHANNEL_AIN0 = 0b01100000      # Single-ended AIN0
CHANNEL_AIN1 = 0b10000000       # Single-ended AIN1
CHANNEL_AIN2 = 0b10100000       # Single-ended AIN2
CHANNEL_AIN3 = 0b11000000       # Single-ended AIN3
CHANNEL_MID_AVDD = 0b11100000   # Mid-supply   P = AVDD/2, N = AVDD/2

GAIN_1X = 0b00000  # Gain = 1 (default)
GAIN_4X = 0b10000  # Gain = 4

DR_20_SPS = 0b0000   # Data rate = 20 SPS (default)
DR_90_SPS = 0b0100   # Data rate = 90 SPS
DR_330_SPS = 0b1000  # Data rate = 330 SPS
DR_1000_SPS = 0b1100  # Data rate = 1000 SPS

CM_SINGLE = 0b00     # Single-shot conversion mode (default)
CM_CONTINUOUS = 0b10  # Continuous conversion mode

VREF_INTERNAL = 0b0  # Internal 2.048V reference (default)
VREF_EXTERNAL = 0b1  # External reference

VREF_INTERNAL_MV = 2048  # Internal reference voltage = 2048 mV
POSITIVE_CODE_RANGE = 0x7FFFFF  # 23 bits of positive range

# TO DO  - implement read config register ,   poll status on drdy if there is no pin connection on raspberry PI


class Adc():
    def __init__(self, address):
        # 1 or 2 for argument I'm not sure
        self.address = address
        # turned off for mock:
        self.i2c = smbus2.SMBus(1)
        self.gain = GAIN_1X
        self.data_rate = DR_20_SPS
        self.conversion_mode = CM_SINGLE
        self.vref = VREF_INTERNAL
        self.channel = CHANNEL_AIN0
        self.current_config = self.read_config()

        self.sensors = {}

        self.exit_flag_set = False

    def start(self):
        self.start_sync()

    def reset(self):
        self.i2c.write_byte(self.address, _COMMAND_RESET)

    def start_sync(self):
        self.i2c.write_byte(self.address, _COMMAND_START_SYNC)

    def powerdown(self):
        self.i2c.write_byte(self.address, _COMMAND_POWERDOWN)

    def set_vref(self, vref):
        self.write_to_config(_VREF_MASK, vref)
        self.vref = vref

    def set_data_rate(self, data_rate):
        self.write_to_config(_DR_MASK, data_rate)
        self.data_rate = data_rate

    def set_gain(self, gain):
        self.write_to_config(_GAIN_MASK, gain)
        self.gain = gain

    def set_conversion_mode(self, mode):
        self.write_to_config(_CM_MASK, mode)
        self.conversion_mode = mode

    def set_channel(self, channel):
        self.write_to_config(_CHANNEL_MASK, channel)
        self.channel = channel

    def write_to_config(self, mask, new_config):
        # this does bitwise operations to put new status into current config so you only have to change one or two bits instead of the whole thing
        '''
        need oto give old config for it to work, either read old config, or guess based on settings
        '''
        # make sure this doesn't cause any errors
        config_message = (self.current_config & ~mask) | new_config
        self.i2c.write_byte_data(
            self.address, _COMMAND_WREG_CONFIG, config_message)
        self.current_config == config_message

    def read_config(self):
        # Need to check this function
        self.i2c.write_byte(self.address, _COMMAND_RREG_CONFIG)
        return self.i2c.read_byte(self.address)

    # not working
    def read_status(self):
        self.i2c.write_byte(self.address, _COMMAND_RREG_STATUS)
        status = self.i2c.read_byte(self.address)
        # need to check this (only returning drdy bit)
        return True if status >= 128 else False

    def read_channel(self, channel):
        self.set_channel(channel)
        if self.conversion_mode == CM_SINGLE:
            self.start_sync()
        # I believe this works???
        data = self.i2c.read_i2c_block_data(self.address, _COMMAND_RDATA, 3)
        return data
        # returns as a list of bytes (integers)

    def convert_to_voltage(self, measurement):
        '''
        measurement should be a list of bytes (one is ok)
        '''
        # if measurement is just an integer
        _measurement = measurement
        if isinstance(_measurement, int):
            _measurement = [_measurement]

        # conver list of bytes to integer
        integer_measurement = int.from_bytes(measurement, "big")

        if self.vref == VREF_INTERNAL:
            # mV or V?
            return integer_measurement/POSITIVE_CODE_RANGE * VREF_INTERNAL_MV
        else:
            # no capability for external voltage reference needed at the moment
            return -1

    def convert_adc_value(self, value, min_real, max_real, min_adc, max_adc):
        # if out of range of expected output from the adc, raise exception -- not really sure what to do here yet
        if value < min_adc or value < max_adc:
            print("CONVERT_ADC_VALUE OUT OF RANGE OF EXPECTED OUTPUT")
            raise Exception  # add specific exception
        return min_real + ((value-min_adc)/(max_adc-min_adc))*(max_real-min_real)

    # only plan on using this for the future
    def read_sensor(self, sensor_name):
        '''
        takes in sensor object
        old_config is there to prevent reading of configuration sensor before setting channel - might save cycles? - will try
        '''
        sensor = self.sensors[sensor_name]
        if sensor == None:
            print("no such sensor in adc class")
        self.set_channel(sensor.channel)
        if self.conversion_mode == CM_SINGLE:
            self.start_sync()
        # I believe this works???
        data = self.i2c.read_i2c_block_data(
            sensor.adc_address, _COMMAND_RDATA, 3)
        return self.convert_adc_value(self.convert_to_voltage(data), sensor.real_min, sensor.real_max, sensor.output_min, sensor.output_max)
        # returns as a list of bytes (integers)

    def add_sensor(self, sensor):
        self.sensors[sensor.name] = sensor

    def read_active_sensors(self):
        sensor_data = {}
        for name, sensor in self.sensors.items():
            if sensor.active == True:
                sensor_data[name] = self.read_sensor(sensor)
        return sensor_data

    def check_active_sensors(self, data):
        for name, sensor in self.sensors.items():
            if sensor.active == True:
                if sensor.check_in_range(data[name]) == False:
                    return False
        return True

    '''
    IF I WANTED TO HAVE A THREAD RUNNING FOR EACH ADC -- UNCLEAR HOW TO SHARE DATA
    def adc_thread(self):
        while self.exit_flag_set == False:
    '''

    def close(self):
        # remember to close!
        # send powerdown command?
        self.i2c.close()

    def read_mock_sensor():
        return time.time


class Sensor():
    def __init__(self, name, channel, output_min, output_max, real_min, real_max, min_range, max_range, active):
        '''
        for channel must use ADC constant
        '''
        self.name = name
        self.channel = channel
        self.output_min = output_min
        self.output_max = output_max
        self.real_min = real_min
        self.real_max = real_max
        self.min_range = min_range
        self.max_range = max_range
        self.active = active

    def check_in_range(self, data):
        if data < self.min_range or data > self.max_range:
            return False
        else:
            return True


if __name__ == "__main__":
    # unit test if connected to ADC 1219

    _adc = Adc(40)
    print(_adc.read_config())
    _adc.set_data_rate(DR_1000_SPS)
    print(_adc.read_config())

    # def unit test
    # unit test should test that bytes can properly be converted
    # 1 write to configuration register
    # 2 read from configuration register
    # print result multiple ways
    # test conversion to integer
