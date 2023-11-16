import socket
import json
import pandas as pd
import matplotlib.pyplot as plt
import threading
import time


################ Responsibilities ###############


# setup plots (plt.show) -- probably in seperate thread


data = open("live_data.txt", '+').read()


HOST = "127.0.0.1"
PORT = 65432

print("BINDING AND LISTENING FOR NEW CONNECTIONS")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

accepting_data = True  # shoulud be controlled by larger start, stop of whole process


def handle_client_recieve(connection, address):
    while accepting_data == True:
        # recieved_data = connection.recv(4096)#.decode()
        recieved_data = connection.recv(4096).decode()
        # if empty (ie client closed connection)
        if not recieved_data:
            break
        # update json or whatever
        print("RECIEVED DATA")
        print(recieved_data)
        if recieved_data == "hello":
            s.sendall("hello".encode())
        else:
            data.write('\n')
            data.write(recieved_data)
            # accepting_data = False    right after receiving first batch???
    connection.close()

# need to clean up this function


def handle_client_command(connection, address):
    while accepting_data == True:
        print("SENDING TEST COMMANDS")
        s.sendall('test'.encode())
        time.sleep(1)


looking_for_clients = True
max_clients = 2
counter = 0
while looking_for_clients == True:
    new_connection, address = s.accept()
    counter += 1
    print(f"Connected to {address}")
    # start thread for handle_client(new_connection)
    client_handler_recieve = threading.Thread(
        target=handle_client_recieve, args=(new_connection, address))
    client_handler_command = threading.Thread(
        target=handle_client_command, args=(new_connection, address))
    print("starting command and recieve threads")
    client_handler_recieve.start()
    client_handler_command.start()
    if counter >= max_clients:
        break


s.close()
data.close()


# threads running - recieving data from multiple raspberry PIs - when recieve:
#       need to update current data files real-time
#       update plots
#       if recived data == "hello"  -- sendall ("hello".encode())
