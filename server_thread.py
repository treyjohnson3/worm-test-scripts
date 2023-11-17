import socket
import json
import threading

#server is to go on main computer


'''
create socket
bind to port
listen for connection
accept connection
recieve stuff
send stuff
recieve close message
close
'''

HOST = "127.0.0.1"
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()



accepting_data = True #shoulud be controlled by larger start, stop of whole process
def handle_client(connection, address):
    while accepting_data == True:
        #recieved_data = connection.recv(4096)#.decode()
        recieved_data = connection.recv(4096).decode()
        #if empty (ie client closed connection)
        if not recieved_data:
            break
        #update json or whatever
        print(recieved_data)
    connection.close()

looking_for_clients = True
max_clients = 2
counter=0
while looking_for_clients == True:
    new_connection, address = s.accept()
    counter +=1
    print(f"Connected to {address}")
    #start thread for handle_client(new_connection)
    client_handler = threading.Thread(target=handle_client, args=(new_connection, address))
    client_handler.start()
    if counter >= max_clients:
        break
s.close()


'''
for handling multiple connections:
def handle client(conn)
    while True:
        recieve data, update
        if not data:
        break
    close conn

counter_max = number of connections expected
loop:
conn =s.acceopt()
counter++
start new thread under function that handles input from client(handle_client(conn))
if counter >= counter_max:
    break
end loop
'''
