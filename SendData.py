import socket, pickle
from typing import List
from grid import *


class SendData:
    """
    """
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), 1234))
        self.socket.listen(5)

    def send_data(self, path: tuple[int, int]):
        """
        path -- the tuple of the x distance and y distance the robot should move
        """
        client_socket, _ = self.socket.accept()
        client_socket.send(pickle.dumps(path)

    def to_zero_one_grid(self, grid: List[List[Tile]]):
        """
        """
        return list(map(lambda row: list(map(lambda tile: 1 if tile.is_obstacle else 0, row)), grid))

