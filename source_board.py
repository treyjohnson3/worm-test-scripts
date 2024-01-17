import threading
import time
import adc
import json
import raspberry_pi_comms
import sys
from enum import Enum
import ctrl_source

adc_list = {}
exit_flag = None
sensor_list = {}
global adc_conversion_mode

# need to make static
HOST = "169.231.172.29"
PORT = 65432
global state
global drdy_wait
global WATCHDOG
global ready

# main idea of this program is that it is organized by process, with each process being its own frunctoin - the proder of these processes being set by the state.

# should have function/class handlers that take care of different tasks to limit coupling from commands/state changes and variable code


class state_list(Enum):
    CONFIGURE = 1
    SSR_120 = 2
    SSR_BATTERY = 3
    BCM_LV = 4
    REVERSE_START = 5
    HV_POWER_ON = 6
    POWER_OFF = 7


def terminate(comm: raspberry_pi_comms.Comms, ):
    print("TEMRINATION CALLED")
    set_state(state_list.POWER_OFF)
    comm.close()
    # close off all of the switches
    # for each adc:
    for ads in adc_list:
        if ads != None:
            ads.close()
    exit_flag.set()  # Set the exit flag to stop the threads
    command_recieve.join()  # Wait for the communication thread to finish
    # GPIO object.cleanup()  # Cleanup GPIO pins
    sys.exit(0)


def set_state(_state: state_list):
    '''
    for actual indendent test of the program -- would have a main thread 
    sequencing when the state changes are happening, but for testing purposes
    we can have the main computer set the state changes. Need to set configuration
    function to run before any state changes such that if we wanted to skip steps and so on
    we won't create obejcts in a state that wouldn't run for a specific test.

    we can define states as to how far down the line in the process we want to go. This
    allows us to control the running of every test straight from the config file. We can 
    add in fake errors, check how the progam/board/process responds. 
    This requres a very indepth definition of states -- dependent on the sequencing of 
    whole procedure. 

    could display curent state/progrss bar on the gui
    '''
    state = _state
    if _state == state_list.CONFIGURE:
        global control
        control = ctrl_source.Source_GPIO()
    if _state == state_list.SSR_120:
        try:
            ready = False
            # turn on 120V voltage and current
            # need to fix system for getting/reading sensors, overly complicated
            # need to activate to start checking every loop
            sensor_list["INPUT_VOLTAGE"]["adc"].activate_sensor(
                "INPUT_VOLTAGE")
            sensor_list["INPUT_CURRENT"]["adc"].activate_sensor(
                "INPUT_CURRENT")

            print(
                f'INPUT_VOLTAGE first read sensor value: {sensor_list["INPUT_VOLTAGE"]["adc"].read_sensor("INPUT_VOLTAGE")}')
            print(
                f'INPUT_CURRENT first read sensor value: {sensor_list["INPUT_CURRENT"]["adc"].read_sensor("INPUT_CURRENT")}')
            # turn on 120V switch
            control.ssr_120("on")

            # not checking in range for the first test

            # if in spec:
            # turn on power supply
            ready = True
        except Exception as e:
            print(f"Exception: {e}")
            print("SSR_120 state failed")
            terminate()

    if _state == state_list.SSR_BATTERY:
        try:
            ready = False

            sensor_list["BATTERY_VOLTAGE"]["adc"].activate_sensor(
                "BATTERY_VOLTAGE")
            sensor_list["BATTERY_CURRENT"]["adc"].activate_sensor(
                "BATTERY_CURRENT")

            # check if victron battery charger v/i is in spec
            print(
                f'First reading of BATTERY_VOLTAGE: {sensor_list["BATTERY_VOLTAGE"]["adc"].read_sensor("BATTERY_VOLTAGE")}')

            # check if battery v/i is in spec
            print(
                f'First reading of BATTERY_CURRENT: {sensor_list["BATTERY_CURRENT"]["adc"].read_sensor("BATTERY_CURRENT")}')

            # not checking if in spec

            # turn on battery switch
            control.power_supply("on")

            ready = True
        except Exception as e:
            print(f"Exception: {e}")
            print("SSR_BATTERY state failed")
            terminate()

    if _state == state_list.BCM_LV:
        ready = False
        # check battery v/i
        # check victron in/out measurement
        # if both are in spec:
        # enable BCM LV switch
        # set ready to true
        pass
    if _state == state_list.REVERSE_START:
        ready = False
        # check BCM LV v/i
        # check BCM reported input voltage
        # enable reverse start
        # wait 5 seconds
        # enable reverse start trigger
        # disbale reverse start trigger
        # check BCM reported in/out voltage
        # if in range -- set ready to true
        # if not in range -- restart reverse start process
        pass
    if _state == state_list.HV_POWER_ON:
        ready = False
        # enable HV switch
        # chekc HV v/i
        # if in range -- set ready to true
        # if not in range -- disable HV power switch - set state to HV_POWER_OFF
        pass
    if state == state_list.MONITOR_AND_CONTROL:
        pass
    if _state == state_list.POWER_OFF:
        control.power_supply("off")
        control.ssr_120("off")
        pass
    print(f"Source Board: state changed to {state}")


def command_recieve(comm: raspberry_pi_comms.Comms):
    while not exit_flag.is_set():
        command = comm.wait_and_recieve_command()
        if command == 'start_sensor_monitoring':
            print("received start command from main computer")
            set_state(state_list.RUNNING)
            # Execute startup action (if needed)
            _sensor_read_thread = threading.Thread(target=sensor_read_thread)
            _sensor_read_thread.start()
            pass
        # configuration message
        elif command[0:2] == "c-":
            set_state(state_list.CONFIGURE)
            config_json = json.loads(command[2:])
            configure_pi(config_json["source_pi"])
        elif command[0:2] == "s-":
            if command[2:] == "CONFIGURE":
                set_state(state_list.CONFIGURE)
            elif command[2:] == "SSR_120":
                set_state(state_list.SSR_120)
            elif command[2:] == "SSR_BATTERY":
                set_state(state_list.SSR_BATTERY)
            elif command[2:] == "BCM_LV":
                set_state(state_list.BCM_LV)
            elif command[2:] == "REVERSE_START":
                set_state(state_list.REVERSE_START)
            elif command[2:] == "HV_POWER_ON":
                set_state(state_list.HV_POWER_ON)
            elif command[2:] == "POWER_OFF":
                set_state(state_list.POWER_OFF)

        elif command == 'test':
            print("successfully recieved test command from main computer")
        elif command == 'stop':
            print("Received stop command. Stopping.")
            terminate()
            break


def sensor_read_thread(comm: raspberry_pi_comms.Comms):
    try:
        ###### continuous/single_shot mode adc data read #######
        if adc_conversion_mode == adc.CM_CONTINUOUS:
            for ads in adc_list:
                ads.start()
        time_counter = time.time()
        while state == state_list.RUNNING:
            ''''''
            ###### 3how are we reading status from multiple sesnors at a time? need to see if we have multiple drdy pins########
            # what sensors do we need to pull multiple times a second? tempeature, voltages, currents
            # honestly thinkging we don't need to check status
            # if checking status, we may need to wait for drdy for each adc sequencially?
            # check timings
            all_adcs_sensor_data = {}
            if adc_conversion_mode == adc.CM_CONTINUOUS:
                if drdy_wait == "read_status":
                    pass
                elif drdy_wait == "read_pin":
                    pass
                elif drdy_wait == "no_wait":
                    pass
                else:
                    print("DIDN'T GIVE/SET PROPER DRDY WAIT")
                pass
            for ads in adc_list:
                latest_data = ads.read_active_sensors()
                # check if in range
                # how do we avoid transient state outliers?
                if WATCHDOG == 1:
                    in_range, name = ads.check_active_sensors(latest_data)
                    if not in_range:
                        print(
                            f"SENSOR {name} out of range, value: {latest_data[name]}")
                        terminate()
                all_adcs_sensor_data.update(latest_data)

            # may want to put this into a seperate thread to avoid IO bottlenecks?
            if time.time() - time_counter >= 1:
                # NEED TO ADD averaging of the data values before sending

                # sending data *from this frame only* every 1 second -- don't believe sending entire batch of data every read is necessary?
                print("SENDING DATA TO MAIN COMPUTER")
                comm.send_json_encoded(all_adcs_sensor_data)
                time_counter = time.time()

    except KeyboardInterrupt:
        print("CTRL C pressed")
        terminate()
    finally:
        terminate()


def configure_pi(config_json: dict):
    # configure adcs
    WATCHDOG = config_json["watchdog"]

    # Note - will probably want to update the sensor file to a csv down the line
    sensor_json = config_json["sensors"]

    # creating adc and sensor objects - repeat for each adc object we are going to be creating
    adc_list[sensor_json[0]["name"]] = adc.Adc(sensor_json[0]["name"], 0x40)
    for i, sensor in sensor_json["adc_1"]["channels"].items():
        sensor_object = adc.Sensor(sensor["name"], "adc_1", i, sensor["output_min"], sensor["output_max"], sensor["real_min"],
                                   sensor["real_max"], sensor["min_range"], sensor["max_range"], True if sensor["active"] == 1 else False)
        adc_list[sensor_json[0]["name"]].add_sensor(sensor_object)
        sensor_list[sensor["name"]] = {
            "sensor_obejct": sensor_object, "adc": adc_list[sensor_json[0]["name"]]}

    adc_list[sensor_json[1]["name"]] = adc.Adc(sensor_json[1]["name"], 0x41)
    for i, sensor in sensor_json["adc_2"]["channels"].items():
        sensor_object = adc.Sensor(sensor["name"], "adc_2", i, sensor["output_min"], sensor["output_max"], sensor["real_min"],
                                   sensor["real_max"], sensor["min_range"], sensor["max_range"], True if sensor["active"] == 1 else False)
        adc_list[sensor_json[1]["name"]].add_sensor(sensor_object)
        sensor_list[sensor["name"]] = {
            "sensor_obejct": sensor_object, "adc": adc_list[sensor_json[1]["name"]]}

    adc_list[sensor_json[2]["name"]] = adc.Adc("adc_3", 0x42)
    for i, sensor in sensor_json["adc_3"]["channels"].items():
        sensor_object = adc.Sensor(sensor["name"], "adc_3", i, sensor["output_min"], sensor["output_max"], sensor["real_min"],
                                   sensor["real_max"], sensor["min_range"], sensor["max_range"], True if sensor["active"] == 1 else False)
        sensor_json[2]["name"].add_sensor(sensor_object)
        sensor_list[sensor["name"]] = {
            "sensor_obejct": sensor_object, "adc": sensor_json[2]["name"]}

    for ads in adc_list.values():
        ads.set_data_rate(config_json["dr_sps"])
        ads.set_conversion_mode(
            adc.CM_CONTINUOUS) if config_json["continuous"] == 1 else ads.set_conversion_mode(adc.CM_SINGLE)
    adc_conversion_mode = adc.CM_CONTINUOUS if config_json["continuous"] == 1 else adc.CM_SINGLE
    drdy_wait = config_json["drdy_wait"]
    print("FULLY CONFIGURED  ---Ready")


if __name__ == "__main__":
    set_state(state_list.CONFIGURE)

    # need to fix order of everything, but also don't want a milliion functions
    # establish socket connection with main computer
    comms = raspberry_pi_comms.Comms(HOST, PORT)
    print("WAITING FOR CONNECTION WITH MAIN COMPUTER")
    comms.wait_for_connection()

    exit_flag = threading.Event()
    command_recieve_thread = threading.Thread(target=command_recieve)
    command_recieve.start()
    # does the end of this kill program? - becuase thread should be going
