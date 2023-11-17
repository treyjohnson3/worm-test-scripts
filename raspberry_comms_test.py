import threading
import RPi.GPIO as GPIO
import time
import socket
import adc
import json
import raspberry_pi_comms
import sys


def terminate():
    print("TEMRINATION CALLED")
    comms.close()
    # for each adc:
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


# Define the sensor reading function (you'll need to replace this with your sensor setup)

def read_sensor():
    # Replace this with code to read your sensor data
    sensor_value = 0  # Replace with actual sensor reading
    return sensor_value

# Define a function for reading the sensor data in a separate thread


HOST = "169.231.172.29"
PORT = 65432
comms = raspberry_pi_comms.Comms(HOST, PORT)


# look for conncetion to main computer - wait loop - loooks for incoming conenction, new loop - waits for startup signal/possible mode?
##### WAIT FOR CONNECTION #####
comms.setup()

# Create and start the communication thread
communication_thread = threading.Thread(target=communication_thread)
communication_thread.start()


time.sleep(5)
print(" ")
print("COMMUNICATIONS TESTS")
print(" ")

# Create an exit flag to gracefully stop the threads
exit_flag = threading.Event()


#################    Setup Communications #########################
print("setting up socket")
HOST = "169.231.184.164"
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
try:
    # Main thread
    i = 0
    while not exit_flag.is_set():
        all_adcs_sensor_data = {}
        # wait for drdy pin status to be true: (in the future will set function handler on drdy pin going low)
        # do this for each adc, currently only works for one

        # read and check all active sensors
        all_adcs_sensor_data[i] = i
        i += 1

        # make this a seperate thread eventually
        # really only need to do this every couple of seconds or so - sends too much will cause backups
        # Send data to main computer
        if time.time() - time1 >= 5:
            # sending a very large amount of data
            print("SENDING DATA TO MAIN COMPUTER")
            comms.send_json_encoded(all_adcs_sensor_data)
            # just for this test
            break


except KeyboardInterrupt:
    pass

finally:
    terminate()
