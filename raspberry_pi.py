import threading
import RPi.GPIO as GPIO
import time
import socket
import adc
import json
import raspberry_pi_comms
import sys


# raspberry pi code loop - it should read sensor data every loop
# and check vs out of bounds values - log which sensor was out of bounds
# plot, accumulate sensor data and send via connection to main computer.
# in the future it will just take sensor data from seesaw and plot/convert to real values.

# when doing for real - checklist
# Need to put in real sensor range json to sensor_range object
# need to convert bytes data to actual readable numbers to check against range from sensors - for effeciency could just check against raw data in the future

##### FOR COMMS TEST #########
'''
def terminate():
    print("TEMRINATION CALLED")
    comms.close()
    #for each adc:
    _adc.close()
    exit_flag.set()  # Set the exit flag to stop the threads
    communication_thread.join()  # Wait for the communication thread to finish
    GPIO.cleanup()  # Cleanup GPIO pins
    sys.exit(0)


def communication_thread():
    # CHECKS FOR COMMANDS FROM COMPUTER
    # NEED TO CHECK IF THE IMPLEMENTATION OF RECV WAITS, AND CONNECT (STARTUP FUNCTION) WAITS ARE SAFE AND EFFECTIVE
    while not exit_flag.is_set():
        command = comms.command_recieve_thread()
        if command == 'start':
            # Execute startup action (if needed)

            pass
        elif command == 'test':
            print("successfully recieved test command from main computer")
        elif command == 'stop':
            print("Received stop command. Stopping.")

            break
'''


# Define the sensor reading function (you'll need to replace this with your sensor setup)

def read_sensor():
    # Replace this with code to read your sensor data
    sensor_value = 0  # Replace with actual sensor reading
    return sensor_value

# Define a function for reading the sensor data in a separate thread


# AT POWER ON or possibly AT SCRIPT RUN via SSH COMMAND FROM MASTER COMPUTER......
#########################################  SETUP ADCs   ############################################################
# set ADC configuration settings
# create an adc object for each adc
_adc = adc.Adc(0x40)
# need to do this for each ADC in use
_adc.set_conversion_mode(adc.CM_SINGLE)
_adc.set_data_rate(adc.DR_1000_SPS)
_adc.set_gain(adc.GAIN_1X)
_adc.set_vref(adc.VREF_INTERNAL)


# Create an exit flag to gracefully stop the threads
exit_flag = threading.Event()

##########################################   SETUP SENSORS   ##########################################


# define sensors
sensor1 = adc.Sensor("testing", "channel",
                     "output_min", "output_max", "real_min", "real_max", "min_range", "max_range", "active")

sensor2 = adc.Sensor("testing", adc.CHANNEL_AIN0, 0, max,
                     0, 1, -1000000, 100000000, True)
# repeat test with one sensor, and with multiple sensors
_adc.add_sensor(sensor2)

'''
#################    Setup Communications #########################

HOST = "127.0.0.1"
PORT = 65432
comms = raspberry_pi_comms.Comms(HOST, PORT)


# look for conncetion to main computer - wait loop - loooks for incoming conenction, new loop - waits for startup signal/possible mode?
##### WAIT FOR CONNECTION #####
comms.setup()

# Create and start the communication thread
communication_thread = threading.Thread(target=communication_thread)
communication_thread.start()
'''


################# MAIN THREAD ##################
# THIS THREAD CHECKS SENSORS AND SENDS DATA TO SOCKET
# probably need to have a seperate thread running for each adc? But there is only one drdy pin?


###### tests ######
# testing simple read
_adc.set_conversion_mode(adc.CM_CONTINUOUS)
_adc.start()
time1 = time.time()
print("RUNNING STATUS READ CHECK")
while True:
    if _adc.read_status() == True:
        print("successfully read drdy status from adc")
        print("channel value: ", _adc.convert_to_voltage(
            _adc.read_channel(adc.CHANNEL_AIN0)))
        break
    if time.time() - time1 > 20:
        print("timed out on simple status read test")
        break

time.sleep(2)
time1 = time.time()
print("RUNNING STATUS READ CHECK for different channel set")
_adc.set_channel(adc.CHANNEL_AIN1)
while True:
    if _adc.read_status() == True:
        print("successfully read drdy status from adc")
        print("channel value: ", _adc.convert_to_voltage(
            _adc.read_channel(adc.CHANNEL_AIN0)))
        break
    if time.time() - time1 > 20:
        print("timed out on simple status read test")
        break

time.sleep(2)

print("RUNNING CM SINGLE CHECK")
print("first value: ", _adc.convert_to_voltage(
    _adc.read_channel(adc.CHANNEL_AIN0)))
_adc.set_conversion_mode(adc.CM_SINGLE)
time.sleep(1)
time1 = time.time()
print("second value: ", _adc.convert_to_voltage(
    _adc.read_channel(adc.CHANNEL_AIN1)))
print("time to execute: ", time.time()-time1)
print("the values should be different")

time.sleep(2)

print("RUNNING TIME TO EXECUTE CHECKS, ALSO RUNNING SENSOR OBJECT CHECKS")
print("THIS IS FOR 20 SPS")
_adc.set_conversion_mode(adc.CM_CONTINUOUS)
_adc.start()
times = []
_adc.set_channel(adc.CHANNEL_AIN0)
time1 = time.time()
time2 = time.time()
while True:
    if time.time() - time1 > 20:
        print("timed out test didn't work")
        break
    if len(times) >= 40:
        break
    if _adc.read_status() == True:
        ssdfsd = _adc.read_active_sensors()
        times.append(time.time()-time2)
        time2 = time.time()
        print(ssdfsd)
if len(times) > 0:
    print("average length of time to read: ", sum(times)/len(times))
    print(times)

time.sleep(2)

print("RUNNIGN TIME TO EXECUTE FOR DIFFERENT DATA RATES")
print("THIS IS FOR 90 SPS")
_adc.set_data_rate(adc.DR_90_SPS)
times = []
_adc.set_channel(adc.CHANNEL_AIN0)
# _adc.start() ???????
time1 = time.time()
time2 = time.time()
while True:
    if time.time() - time1 > 20:
        print("timed out test didn't work")
        break
    if len(times) >= 40:
        break
    if _adc.read_status() == True:
        ssdfsd = _adc.read_active_sensors()
        times.append(time.time()-time2)
        time2 = time.time()
        print(ssdfsd)
if len(times) > 0:
    print("average length of time to read: ", sum(times)/len(times))
    print(times)


time.sleep(2)

print("RUNNIGN TIME TO EXECUTE FOR DIFFERENT DATA RATES")
print("THIS IS FOR 330")
_adc.set_data_rate(adc.DR_90_SPS)
times = []
_adc.set_channel(adc.CHANNEL_AIN0)
_adc.start()
time1 = time.time()
time2 = time.time()
while True:
    if time.time() - time1 > 20:
        print("timed out test didn't work")
        break
    if len(times) >= 40:
        break
    if _adc.read_status() == True:
        ssdfsd = _adc.read_active_sensors()
        times.append(time.time()-time2)
        time2 = time.time()
        print(ssdfsd)
if len(times) > 0:
    print("average length of time to read: ", sum(times)/len(times))
    print(times)

time.sleep(2)

print("RUNNIGN TIME TO EXECUTE FOR DIFFERENT DATA RATES")
print("THIS IS FOR 1000 SPS")
_adc.set_data_rate(adc.DR_90_SPS)
times = []
_adc.set_channel(adc.CHANNEL_AIN0)
_adc.start()
time1 = time.time()
time2 = time.time()
while True:
    if time.time() - time1 > 20:
        print("timed out test didn't work")
        break
    if len(times) >= 40:
        break
    if _adc.read_status() == True:
        ssdfsd = _adc.read_active_sensors()
        times.append(time.time()-time2)
        time2 = time.time()
        print(ssdfsd)
if len(times) > 0:
    print("average length of time to read: ", sum(times)/len(times))
    print(times)


###### NEED TO ADD DRDY IRQ FUNCTION HANDLER TEST #########

time.sleep(2)
print("STARTING DRDY FUNCTION HANDLER TEST")

# should also test for setting channel to different channel than the one being used
_adc.set_channel(adc.CHANNEL_AIN0)


def irq_falling(channel):
    print("DRDY PIN FELL....")
    _adc.convert_to_voltage(_adc.read_channel(adc.CHANNEL_AIN0))
    print("data ready ", channel)


IRQ_GPIO_PIN = 4  # set pin for drdy
print("set drdy pin to ", IRQ_GPIO_PIN)
IRQ_EDGE = GPIO.FALLING

GPIO.setmode(GPIO.BCM)
GPIO.setup(IRQ_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(IRQ_GPIO_PIN, IRQ_EDGE, callback=irq_falling)

time1 = time.time()
while True:
    if time.time()-time1 >= 20:
        break
    time.sleep(1)

GPIO.cleanup()
_adc.close()


'''


time.sleep(5)
print(" ")
print("COMMUNICATIONS TESTS")
print(" ")


#################    Setup Communications #########################
print("setting up socket")
HOST = "127.0.0.1"
PORT = 65432
comms = raspberry_pi_comms.Comms(HOST, PORT)

print("setting up connection")
# look for conncetion to main computer - wait loop - loooks for incoming conenction, new loop - waits for startup signal/possible mode?
##### WAIT FOR CONNECTION #####
comms.setup()
print("connection established")

# Create and start the communication thread, recieves commands from main computer
communication_thread = threading.Thread(target=communication_thread)
communication_thread.start()
print("Started recieve thread, waiting for test commands to come in")
print("trying check comms: ")
print(comms.check_comms())
time.sleep(5)

time1 = time.time()
_adc.start()
try:
    # Main thread
    i = 0
    while not exit_flag.is_set():
        all_adcs_sensor_data = {}
        # wait for drdy pin status to be true: (in the future will set function handler on drdy pin going low)
        # do this for each adc, currently only works for one
        if _adc.read_status() == False:
            continue

        # read and check all active sensors
        all_adcs_sensor_data[i] = _adc.read_active_sensors()
        i+=1

        ''
        DONT NEED TO CHECK SENSORS FOR THIS TEST
        if _adc.check_active_sensors(all_adcs_sensor_data) == False:
            terminate()
            break
            # need to add info so that we know what sensor was out of range
        ''

        #make this a seperate thread eventually
        # really only need to do this every couple of seconds or so - sends too much will cause backups 
        # Send data to main computer
        if time.time() - time1 >=5:
            #sending a very large amount of data
            print("SENDING DATA TO MAIN COMPUTER")
            comms.send_json_encoded(all_adcs_sensor_data)
            #just for this test
            break


except KeyboardInterrupt:
    pass

finally:
    terminate()
'''
