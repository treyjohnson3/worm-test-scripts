import threading
import RPi.GPIO as GPIO
import time
import adc
import json
import raspberry_pi_comms
import sys
from enum import Enum

adc_list = []
exit_flag = None
adc_conversion_mode = adc.CM_SINGLE

# need to make static
HOST = "169.231.172.29"
PORT = 65432
global state


class state_list(Enum):
    INITIALIZE = 1
    STARTUP = 2
    RUNNING = 3
    HIBERNATE = 4
    SHUTDOWN = 5
    EMERGENCY_SHUTDOWN = 6


def terminate(comm: raspberry_pi_comms.Comms, ):
    print("TEMRINATION CALLED")
    comm.close()
    # for each adc:
    for ads in adc_list:
        if ads != None:
            ads.close()
    exit_flag.set()  # Set the exit flag to stop the threads
    command_recieve.join()  # Wait for the communication thread to finish
    GPIO.cleanup()  # Cleanup GPIO pins
    sys.exit(0)


def command_recieve(comm: raspberry_pi_comms.Comms):
    while not exit_flag.is_set():
        command = comm.wait_and_recieve_command
        if command == 'start':
            print("received start command from main computer")
            state = state_list.RUNNING
            # Execute startup action (if needed)
            _sensor_read_thread = threading.Thread(target=sensor_read_thread)
            _sensor_read_thread.start()
            pass
        elif command == 'test':
            print("successfully recieved test command from main computer")
        elif command == 'stop':
            print("Received stop command. Stopping.")
            terminate()
            break


def sensor_read_thread(comm: raspberry_pi_comms.Comms):
    try:
        ###### continuous/single_shot mode adc data read #######
        for ads in adc_list:
            ads.start()
        time_counter = time.time()
        perf_time = time.perf_counter()  # just for testing
        while state == state_list.RUNNING:
            ''''''
            all_adcs_sensor_data = {}
            if adc_conversion_mode == adc.CM_CONTINUOUS:
                # gpio wait for drdy pin to fall
                # or just check status
                # not sure how to best do check status -- thinking we probably don't need it.
                pass
            for ads in adc_list:
                latest_data = ads.read_active_sensors()
                # check if in range
                in_range, name = ads.check_active_sensors(latest_data)
                if not in_range:
                    print(
                        f"SENSOR {name} out of range, value: {latest_data[name]}")
                    terminate()
                all_adcs_sensor_data.update(latest_data)

            print(
                f"Time to read sensors: {time.perf_counter()-perf_time}. This coresponds to {1/(time.perf_counter()-perf_time)} reads per second")
            perf_time = time.perf_counter()
            print(all_adcs_sensor_data)

            if time.time() - time_counter >= 1:
                # sending data *from this frame only* every 5 seconds -- don't believe sending entire batch of data is necessary?
                print("SENDING DATA TO MAIN COMPUTER")
                comm.send_json_encoded(all_adcs_sensor_data)
                # just for this test
                time_counter = time.time()
                break

    except KeyboardInterrupt:
        print("CTRL C pressed")
        terminate()
    finally:
        terminate()


if __name__ == "__main__":
    state = state_list.INITIALIZE

    # Note - will probably want to update the sensor file to a csv down the line
    with open("sensors.json", "r") as json_file:
        sensor_json = json.load(json_file)

    # creating adc and sensor objects - repeat for each adc object
    _adc = adc.Adc(0x40)
    adc_list.append(_adc)
    for i, sensor in sensor_json["adc_1"]["channels"].items():
        _adc.add_sensor(adc.Sensor(sensor["name"], i, sensor["output_min"], sensor["output_max"], sensor["real_min"],
                        sensor["real_max"], sensor["min_range"], sensor["max_range"], True if sensor["active"] == 1 else False))

    '''
    # establish socket connection with main computer
    comms = raspberry_pi_comms.Comms(HOST, PORT)
    comms.wait_for_connection()

    exit_flag = threading.Event()
    command_recieve_thread = threading.Thread(target=command_recieve)
    command_recieve.start()
    # does the end of this kill program? - becuase thread should be going
    '''
