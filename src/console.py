import socket
from config import *
from client import *

if __name__ == 'main':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    while True:
        
        command = input('>> ').split()

        match command[0]:

            case __:
                print('Invalid command')
                continue