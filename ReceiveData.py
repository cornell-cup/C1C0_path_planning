import socket
import pickle
from typing import List, Dict
from Tile import *
from tkinter import *


class ReceiveData:
    def __init__(self, grid: List[List[Tile]], canvas: Canvas, tile_dict: Dict[Tile, int]):
        self.data_arr = []
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostname(), 1234))
        self.grid: Grid = grid
        self.canvas: Canvas = canvas
        self.tile_dict: Dict[Tile, int] = tile_dict

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

    def grid_update(self):
        print('starting grid update')
        new_grid = self.data_transfer()
        for row in range(len(new_grid)):
            for col in range(len(new_grid[row])):
                print((row, col))
                if new_grid[row][col] == 0:
                    self.grid[row][col].is_obstacle = False
                    self.canvas.itemconfig(
                        self.grid[row][col], outline=background_color, fill=background_color)
                else:
                    self.grid[row][col].is_obstacle = True
                    self.canvas.itemconfig(
                        self.grid[row][col], outline=obstacle_color, fill=obstacle_color)
        print('ending grid update')
