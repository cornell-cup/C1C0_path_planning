import socket
import pickle
from typing import List, Dict
from Tile import *
from tkinter import *


class ReceiveData:
    def __init__(self):
        self.dist = ()
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostname(), 1234))


    def data_transfer(self):
        data = []
        print('starting data transfer')
        while True:
            packet = self.socket.recv(4096)
            if not packet:
                break
            data.append(packet)

        data_arr = pickle.loads(b"".join(data))
        print('finished data transfer')
        return data_arr
