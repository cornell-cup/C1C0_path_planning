import socket
from tkinter import *
from Consts import *
from grid import Grid

class ReceiveData:
    def __init__(self, inputMap):
        self.message = []
        self.grid = inputMap
        self.tile_dict = None
        self.canvas = None

    def convert_data(self, full_msg):
        res = []
        curr = []
        for i in full_msg:
            if curr != [] and i == "[":
                continue
            elif curr != [] and i == "]":
                res.append(curr)
                curr = []
                continue
            elif i == ",":
                continue
            elif i != "[" and i != "]" and i != ",":
                curr.append(int(i))
        return res
    
    def data_transfer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostname(), 1234))
        
        full_msg = ''
        while True:
            msg = s.recv(8)
            if len(msg) <= 0:
                break
            full_msg += msg.decode("utf-8")
        self.message = convert_data(full_msg)
        
    def map_update(self):
        for i in range(self.message):
            for j in range(self.message[0]):
                if self.message[i][j] != 0:
                    curr_tile = self.grid.grid[j][i]
                    curr_rec = self.tile_dict[curr_tile]
                    self.canvas.itemconfig(
                        curr_rec, outline="#ffCC99", fill="#ffCC99")