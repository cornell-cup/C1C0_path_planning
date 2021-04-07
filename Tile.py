from Consts import *


class Tile:
    top, mid, bottom, lidar = 0, 1, 2, 3

    def __init__(self, x, y, row, col, isObstacle=False, isBloated=False, isKnown=False):
        """
        Initialize a tile centered at x coordinate [x] and y coordinate [y].
        If [isObstacle] is True, the tile is initialized as an obstacle, else Tile is
        marked as free space, [isObstacle] is False by default.
        """
        self.obstacle_score = [0, 0, 0, 0]
        self.bloat_score = [0, 0, 0, 0]
        self.bloat_tiles = []
        self.is_found = False
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.is_obstacle = isObstacle
        self.is_bloated = isBloated

    def updateStatus(self):
        for score in self.obstacle_score:
            self.is_obstacle = bool(self.is_obstacle or score)

    def get_color(self):
        """
            Returns
                (string): string representation of hex code for the color of the tile
        """
        if self.is_bloated:
            color = bloated_color
        elif self.is_obstacle:
            color = obstacle_color
        else:
            color = background_color
        return color
