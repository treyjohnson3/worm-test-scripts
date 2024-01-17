import socket
import json
import time
import threading
from socketserver import StreamRequestHandler, TCPServer

# IN THIS VERSION, THE RASPBERRY PI PLAYS THE ROLE OF THE SERVER

# test raspberry pi's current ip address
#  -- need to make static
HOST = "169.231.172.29"
PORT = 65432


class Comms():
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))

        self.failed_connection_buffer_num = 10
        self.main_connection = None

    def wait_for_connection(self):
        self.s.listen(self.failed_connection_buffer_num)
        self.main_connection, address = self.s.accept()

    def send_json_encoded(self, json_message):
        '''
        with json encoded (utf-8 default)
        json_message should be a dictionary
        '''
        data_to_send = json.dumps(json_message).encode()
        self.sendall(data_to_send)

    def send_message(self, message):
        self.sendall(message.encode())

    def check_comms(self):
        # send hello message - wait for echo back
        # .encode() could be wasting cycles?
        self.main_connection.sendall("hello".encode())
        data = self.recv(1024).decode()
        return data == "hello"

    def wait_and_recieve_command(self):
        # Receive commands from the main computer
        command = self.recv(4096).decode()
        if command == "hello":
            self.send_message("hello".encode())
        print(f"Received command {command}")
        return command

    def close(self):
        self.main_connection.close()


class DumpHandler(StreamRequestHandler):
    def handle(self) -> None:
        """receive json packets from client"""
        print('connection from {}:{}'.format(*self.client_address))
        try:
            while True:
                data = self.rfile.readline()
                if not data:
                    break
                print('received', data.decode().rstrip())

        finally:
            print('disconnected from {}:{}'.format(*self.client_address))


def main() -> None:
    server_address = ("169.231.172.29", 65432)
    print('starting up on {}:{}'.format(*server_address))
    with TCPServer(server_address, DumpHandler) as server:
        print('waiting for a connection')
        server.serve_forever()
