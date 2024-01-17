import socket
import json
import time
import threading

# IN THIS VERSION, THE RASPBERRY PI PLAYS THE ROLE OF THE SERVER

# Thinking should make commands an enum, rather than a string?

# test raspberry pi's current ip address
#  -- need to make static
# each pi has a different ip address
HOST = "169.231.172.29"
PORT = 65432


class Comms():
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.max_num_tries = 10

    def setup(self):
        num_tries = 0
        while num_tries < self.max_num_tries:
            num_tries += 1
            try:
                print(f"Trying to connect to pi at {HOST}, {PORT}")
                self.s.connect((HOST, PORT))
                break
            except OSError:
                print(f"attempt at connection to pi at {HOST}, {PORT} FAILED")
                print("attempting to connect again in 1 second")
                time.sleep(1)
        else:
            raise Exception(
                f"Attempt to connect {HOST} and {PORT} failed after {num_tries} tries")

    def send_command(self, command):
        '''
        command should be a string
        json_message should be a dictionary
        '''
        self.s.sendall(command.encode())

    def check_comms(self):
        # send hello message - wait for echo back
        # .encode() could be wasting cycles?
        self.s.sendall("hello".encode())
        data = self.s.recv(1024).decode()
        return data == "hello"

    def wait_and_recieve_data(self):
        # Receive commands from the main computer
        data = self.s.recv(4096).decode()
        if data == "hello":
            self.s.send_command("hello")
        if data == None:
            self.close()
            return "terminate"
        return data

    def close(self):
        self.s.close()
