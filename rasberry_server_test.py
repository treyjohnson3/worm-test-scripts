import socket
import threading
import time
import raspberry_pi_comms


def communication_thread(new_connection):
    # CHECKS FOR COMMANDS FROM COMPUTER
    # NEED TO CHECK IF THE IMPLEMENTATION OF RECV WAITS, AND CONNECT (STARTUP FUNCTION) WAITS ARE SAFE AND EFFECTIVE
    while not exit_flag.is_set():
        command = new_connection.recv(1024).decode()
        print(command)
        if command == 'start':
            # Execute startup action (if needed)

            pass
        elif command == 'test':
            print("successfully recieved test command from main computer")
        elif command == 'stop':
            print("Received stop command. Stopping.")

            break


HOST = "169.231.172.29"
PORT = 65432


time.sleep(5)
print(" ")
print("COMMUNICATIONS TESTS")
print(" ")

# Create an exit flag to gracefully stop the threads
exit_flag = threading.Event()

print("BINDING AND LISTENING FOR NEW CONNECTIONS")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(20)
new_connection, address = s.accept()


# Create and start the communication thread, recieves commands from main computer
communication_thread = threading.Thread(
    target=communication_thread, args=(new_connection))
communication_thread.start()
print("Started recieve thread, waiting for test commands to come in")
print("trying check comms: ")
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
            new_connection.sendall(
                "test ljhfdshflksadhfjasdh;kjbasd;kjfb;askjdbf;kasjdbfh;kjasbdf;kajsbdf;kjasbdf;kajsbdf;kajsdbf;kajsdbfkjdsbfkjasdbfk".encode())
            # just for this test
            break


except KeyboardInterrupt:
    s.close()

s.close()
