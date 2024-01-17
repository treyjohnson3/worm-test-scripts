import socket
import json
import time
import threading

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
        data_to_send = json.dumps(json_message)
        self.send(data_to_send)

    def send_message(self, message):
        self.send(message)

    def check_comms(self):
        # send hello message - wait for echo back
        # .encode() could be wasting cycles?
        self.main_connection.send("hello")
        data = self.recieve()
        return data == "hello"

    def wait_and_recieve_command(self):
        # Receive commands from the main computer
        command = self.recieve()
        if command == "hello":
            self.send_string("hello")
        print(f"Received command {command}")
        return command

    def send(self, data):
        # send the length of the serialized data first
        self.main_connection.send('%d\n' % len(data))
        # send the serialized data
        self.main_connection.sendall(data)

    def recieve(self):
        # read the length of the data, letter by letter until we reach EOL
        length_str = ''
        char = self.main_connection.recv(1)
        while char != '\n':
            length_str += char
            char = self.main_connection.recv(1)
        total = int(length_str)
        # use a memoryview to receive the data chunk by chunk efficiently
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            recv_size = self.s.recv_into(
                view[next_offset:], total - next_offset)
            next_offset += recv_size
        return view.tobytes()

    def close(self):
        self.main_connection.close()
