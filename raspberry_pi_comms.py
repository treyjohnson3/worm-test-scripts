import socket
import json
import time
import threading

HOST = "127.0.0.1"
PORT = 65432


class Comms():
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setup(self):
        self.s.connect((HOST, PORT))

    def send_json_encoded(self, json_message):
        '''
        with json encoded (utf-8 default)
        json_message should be a dictionary
        '''
        data_to_send = json.dumps(json_message).encode()
        self.s.sendall(data_to_send)

    def send_message(self, message):
        self.s.sendall(message.encode())

    def check_comms(self):
        # send hello message - wait for echo back
        # .encode() could be wasting cycles?
        self.s.sendall("hello".encode())
        data = self.s.recv(4096).decode()
        return data == "hello"

    def command_recieve_thread(self):
        # Receive commands from the main computer
        command = self.s.recv(1024).decode()
        return command

    def close(self):
        self.s.close()
