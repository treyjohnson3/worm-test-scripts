"""
Python Code responsible for creating a remote ssh connection into the computers and running the main python scripts

TODO: Add server uptime on error (server should just restart on ctrl c rather than having to manually restart it)


"""


import paramiko
import signal
import sys
import threading
import time
import select
import json


class ssh_connect:
    def __init__(self, json_config):
        self.host = json_config['host']
        self.user = json_config['user']
        self.password = json_config['password']
        self.python_script_path = json_config['python_script_path']
        self.python_exe_path = json_config['python_exe_path']

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, username=self.user,
                         password=self.password, timeout=5)  # TODO: Add timeout

        self.channel = self.ssh.get_transport().open_session()
        self.channel.get_pty()

    def startup_execution(self):
        self.channel.exec_command(
            f"{self.python_exe_path} -u {self.python_script_path}")

'''
class SSHManager:
    def __init__(self):
        self.connections = []
        self.thread_running = True
        self.exit_flag = False

    def add_connection(self, json_config):
        try:
            print("Adding Connection")
            connection = ssh_connect(json_config)
            self.connections.append(connection)
            print(f"Connection Established with {json_config['host']}")
            return True
        except:
            print(f"ERROR: Unable to connect to {json_config['host']}")
            return False

    def read_output(self, ssh_output):
        # print("Thread Started")
        while self.thread_running:
            channels = [conn.channel for conn in self.connections]
            if channels:
                try:
                    if self.exit_flag:
                        for conn in self.connections:
                            conn.channel.send(u"\x03")
                        self.exit_flag = False
                    readable, _, _ = select.select(channels, [], [], 0.0)
                    for channel in readable:
                        if channel.recv_ready():
                            output = channel.recv(1024).decode('utf-8')
                            if len(output) > 2:

                                if channel.get_transport().getpeername()[0] == '192.168.1.71':
                                    ssh_output.setTextColor(QColor(0, 255, 0))
                                elif channel.get_transport().getpeername()[0] == '192.168.1.56':
                                    ssh_output.setTextColor(QColor(255, 0, 0))
                                else:
                                    ssh_output.setTextColor(QColor(0, 0, 255))
                                ssh_output.append(
                                    f"Output from {channel.get_transport().getpeername()}: {output}")
                                cursor = ssh_output.textCursor()
                                cursor.movePosition(
                                    QtGui.QTextCursor.MoveOperation.End)
                                ssh_output.setTextCursor(cursor)

                        if channel.exit_status_ready():
                            channels.remove(channel)
                except:
                    print("Error")
                    for conn in self.connections:
                        conn.channel.send(u"\x03")
                    pass


"""
# TODO: Might need to make multithreaded
    def read_output(self):
        while True:
            try:
                if self.channel.exit_status_ready():
                    break
                #print(count)
                    
                rl, wl, xl = select.select([self.channel], [], [], 0.0)
                if len(rl) > 0:
                    print(self.channel.recv(1024).decode())
            except:
                print("Error")
                self.channel.send(u"\x03")
                pass


if __name__ == "__main__":

    # p_remote_python_script = r'C:\Users\Phoebe\Desktop\WattsontheMoon-v2\control_phoebe\test_server.py'

    # l_remote_python_script = r'/home/periscope/Code/BCM/control_V2/main/test_server.py'

    config = json.load(
        open(r"C:\Users\Lubin\Desktop\code\WOTM_GUI\config.json"))

    manager = SSHManager()

    manager.add_connection(config['phoebe'])
    # manager.add_connection(l_remote_host, l_remote_user, l_remote_password, l_remote_python_script, l_python_exe_path)

    print("Connections Established")

    manager.read_output()
'''