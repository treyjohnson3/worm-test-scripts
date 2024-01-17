import RPi.GPIO as GPIO


class Source_GPIO:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.ssr_120_switch_pin = 4
        self.battery_swtich_pin = 5
        self.heater0_switch_pin = 6
        self.heater1_switch_pin = 7
        self.BCM_LV_switch_pin = 8
        self.HV_switch_pin = 9
        self.rev_start_enable_pin = 10
        self.rev_start_trigger_pin = 11
        self.reset_adc_pin = 12
        self.therm0_enable_pin = 13
        self.therm1_enable_pin = 14
        self.therm_A0_pin = 15
        self.therm_A1_pin = 16
        self.therm_A2_pin = 17
        self.therm_A3_pin = 18
        self.CP_enable_pin = 19
        self.drdy_pin = 20

        GPIO.setup(self.ssr_120_switch_pin, GPIO.OUT)
        GPIO.setup(self.battery_swtich_pin, GPIO.OUT)
        GPIO.setup(self.heater0_switch_pin, GPIO.OUT)
        GPIO.setup(self.heater1_switch_pin, GPIO.OUT)
        GPIO.setup(self.BCM_LV_switch_pin, GPIO.OUT)
        GPIO.setup(self.HV_switch_pin, GPIO.OUT)
        GPIO.setup(self.rev_start_enable_pin, GPIO.OUT)
        GPIO.setup(self.rev_start_trigger_pin, GPIO.OUT)
        GPIO.setup(self.reset_adc_pin, GPIO.OUT)
        GPIO.setup(self.therm0_enable_pin, GPIO.OUT)
        GPIO.setup(self.therm1_enable_pin, GPIO.OUT)
        GPIO.setup(self.therm_A0_pin, GPIO.OUT)
        GPIO.setup(self.therm_A1_pin, GPIO.OUT)
        GPIO.setup(self.therm_A2_pin, GPIO.OUT)
        GPIO.setup(self.therm_A3_pin, GPIO.OUT)
        GPIO.setup(self.CP_enable_pin, GPIO.OUT)
        # drdy?

    def ssr_120(self, state):
        if state == "on":
            # what is the hv present line?
            GPIO.output(self.ssr_120_switch_pin, GPIO.HIGH)
            print("Source Board Control: set ssr_120 pin to HIGH")
            # GPIO.output(self.hv_line_present_pin, GPIO.HIGH)
            return "ssr_120 on"
        elif state == "off":
            GPIO.output(self.ssr_120_switch_pin, GPIO.LOW)
            print("Source Board Control: set ssr_120 pin to LOW")
            # GPIO.output(self.hv_line_present_pin, GPIO.LOW
            #            )
            return "ssr_120 off"

    def bcm_lv_feed(self, state):
        if state == "on":
            GPIO.output(self.BCM_LV_switch_pin, GPIO.HIGH)
            print("Source Board Control: set BCM_LV pin to HIGH")
            return "bcm_lv_feed on"
        elif state == "off":
            GPIO.output(self.BCM_LV_switch_pin, GPIO.LOW)
            print("Source Board Control: set BCM_LV pin to LOW")
            return "bcm_lv_feed off"

    def ssr_800(self, state):
        if state == "on":
            GPIO.output(self.HV_switch_pin, GPIO.HIGH)
            print("Source Board Control: set ssr_800 pin to HIGH")
            return "ssr_400 on"
        elif state == "off":
            GPIO.output(self.HV_switch_pin, GPIO.LOW)
            print("Source Board Control: set ssr_800 pin to LOW")
            return "ssr_400 off"

    def power_supply(self, state):
        if state == "on":
            GPIO.output(self.battery_swtich_pin, GPIO.HIGH)
            print("Source Board Control: set power_supply pin to HIGH")
        elif state == "off":
            GPIO.output(self.battery_swtich_pin, GPIO.LOW)
            print("Source Board Control: set power_supply pin to LOW")
        else:
            print("Error: Unrecognized state")

    def reverse_start(self):
        # do reverse start
        pass

    def heater_swtich(self, state):
        if state == "on":
            GPIO.output(self.heater0_switch_pin, GPIO.HIGH)
            print("Source Board Control: set heater_0 pin to HIGH")
            GPIO.output(self.heater1_switch_pin, GPIO.HIGH)
            print("Source Board Control: set heater_1 pin to HIGH")
        elif state == "off":
            GPIO.output(self.heater1_switch_pin, GPIO.LOW)
            print("Source Board Control: set heater_1 pin to HIGH")
            GPIO.output(self.heater0_switch_pin, GPIO.LOW)
            print("Source Board Control: set heater_0 pin to HIGH")
        else:
            print("Error: Unrecognized state")


""" # BCM Not in use for these tests
class BCM:
    def __init__(self):
        self.i2c = SMBus(1) 
        self.i2caddress = 0x50

        # Variables
        self.STATUS_WORD = 0x78
        self.STATUS_BYTE = 0x79
        self.STATUS_IOUT = 0x7B
        self.STATUS_INPUT = 0x7C
        self.STATUS_TEMPERATURE = 0x7D
        self.STATUS_MFR_SPECIFIC = 0x80



    # Reads all from BCM
    # Outputs a list of two integers
    def read_bcm(self, i2c, i2c_cmd):
        bcm_data = i2c.read_i2c_block_data(self.i2caddress, i2c_cmd)
        bcm_data = bcm_data[0:2] # Grabs first two elements
        return bcm_data
    
    # Queries the BCM for all status data
    # Outputs list of all status data
    def query_bcm_status(self):
        bcm_list = []

        bcm_list.extend(self.read_bcm(self.i2c, self.STATUS_WORD))
        bcm_list.extend(self.read_bcm(self.i2c, self.STATUS_BYTE))
        bcm_list.extend(self.read_bcm(self.i2c, self.STATUS_IOUT))
        bcm_list.extend(self.read_bcm(self.i2c, self.STATUS_INPUT))
        bcm_list.extend(self.read_bcm(self.i2c, self.STATUS_TEMPERATURE))
        bcm_list.extend(self.read_bcm(self.i2c, self.STATUS_MFR_SPECIFIC))

        return bcm_list

       """
