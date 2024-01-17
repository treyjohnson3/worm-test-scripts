import json
import threading
import time
import sys
import computer_side_comms
import ssh_connection
import data_handler
from datetime import datetime
import tkinter as tk
import gui

# need to consider how to handle race conditions - this code is updating, accessing data constantly from multiple threads

# raspberry pi ip -need to make status
source_HOST = "169.231.172.29"
source_PORT = 65432

load_HOST = ""
load_PORT = 00000

phoebe_HOST = ""
phoebe_PORT = 00000

active_comms = {}
active_threads = []


def terminate():
    print("TERMINATION CALLED")
    exit_flag.set()  # Set the exit flag to stop the threads
    for thread in active_threads:
        thread.join()
    for computer in active_comms:
        computer.join()
    sys.exit(0)


def send_command(command: str):
    for computer in active_comms.values():
        computer.send_command(command)


def data_recieve_thread(communication: computer_side_comms.Comms):
    while not exit_flag.is_set():
        message = communication.wait_and_recieve_data()
        # for first test:
        print(message)
        if message == None:
            print("load socket closed, terminating sequence")
            terminate()
        elif message[0] == "m":  # of form m-command
            if message == "m-some status message":
                pass
        else:
            time_elapsed = (datetime.now-start_time).strftime(
                "%H:%M:%S")
            message = json.loads(message)
            _data_handler.update_data(time_elapsed, message)
            # given data -- update plots and write it to file
            pass
    pass


# only for inital testing, later on the onboard computers should handle this
def sequence_thread(config: dict):
    print("MAIN_COMPUTER: STARTING SEQUENCE")
    time.sleep(5)

    # communications test:
    print("MAIN_COMPUTER: CHECKING COMMUNICATION")
    for comms in active_comms:
        if comms.check_comms() == False:
            print("COMMUNICATIONS TEST FAILED")
            terminate()
            return

    # c-json --> config command
    time.sleep(5)
    # sending configuration info to computers.
    print("SENDING CONFIGURATION INFO/COMMAND TO ACTIVE COMPUTERS")
    send_command("c-" + json.dumps(config).encode())
    time.sleep(10)

    # other messages
    # Main computer runs sequencing for the boards - sends via state commands
    # CONFIGURE = 1, SSR_120 = 2, SSR_BATTERY = 3, BCM_LV = 4, REVERSE_START = 5, HV_POWER_ON = 6, POWER_OFF = 7
    # send_command("s-some state change")

    ###### STARTUP ######
    states_dict = config["states"]

    for state, value in states_dict.items():
        if value == 1:
            print(f"MAIN COMPUTER setting state: {state}")
            send_command("s-{state}")
            time.sleep(5)

    pass


if __name__ == "__main__":
    # setup gui, plots, objects, other stuff

    with open("testing_config.json", "r") as file:
        testing_config = json.load(file)

    # load info from config file
    source_HOST = testing_config["source"]["host"]
    source_PORT = testing_config["source"]["port"]

    load_HOST = testing_config["load"]["host"]
    load_PORT = testing_config["load"]["port"]

    phoebe_HOST = testing_config["phoebe"]["host"]
    phoebe_PORT = testing_config["phoebe"]["port"]

    # probably not doing SSH command in first test
    # send ssh commands -- only if active in testing_config file
    '''
    if testing_config["source"]["active"] == 1:
        source_ssh = ssh_connection.ssh_connect(testing_config["source"])
        source_ssh.startup_execution()
    if testing_config["load"]["active"] == 1:
        load_ssh = ssh_connection.ssh_connect(testing_config["load"])
        load_ssh.startup_execution()
    if testing_config["phoebe"]["active"] == 1:
        phoebe_ssh = ssh_connection.ssh_connect(testing_config["phoebe"])
        phoebe_ssh.startup_execution()
    '''

    # let them start up
    time.sleep(5)

    # raspberry pi's should be started up and operating before connection with main comptuer established
    # should be issuing commands to change the state of the pies to commence different sequences
    exit_flag = threading.Event()
    # creating computer objects according to config file
    if testing_config["source"]["active"] == 1:
        source = computer_side_comms.Comms(source_HOST, source_PORT)
        active_comms["source"] = source

    if testing_config["load"]["active"] == 1:
        load = computer_side_comms.Comms(load_HOST, load_PORT)
        active_comms["load"] = load

    if testing_config["phoebe"]["active"] == 1:
        phoebe = computer_side_comms.Comms(phoebe_HOST, phoebe_PORT)
        active_comms["phoebe"] = phoebe

    _data_handler = data_handler.DataHandler(0, len(active_comms))
    start_time = datetime.now()

    # starting computer communication threads
    time.sleep(5)
    for computer in active_comms.values():
        computer.setup()
        thread = threading.Thread(
            target=data_recieve_thread, args=(computer))
        active_threads.append(thread)
        thread.start()

    sequence_thread = threading.Thread(
        target=sequence_thread, args=(testing_config))
    active_threads.append(sequence_thread)
    sequence_thread.start()

    # create gui only if active in testing_config file
    if testing_config["main computer setting"]["gui"] == 1:
        app = gui.Gui()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.start_gui()
