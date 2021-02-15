from Consts import *


class Tile:
    def __init__(self, x, y, row, col, isObstacle=False, isBloated=False, isKnown=False):
        """
        Initialize a tile centered at x coordinate [x] and y coordinate [y].
        If [isObstacle] is True, the tile is initialized as an obstacle, else Tile is
        marked as free space, [isObstacle] is False by default.
        """
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.isObstacle = isObstacle
        self.isBloated = isBloated

    def get_color(self):
        """
            Returns
                (string): string representation of hex code for the color of the tile
        """
        if self.isBloated:
            color = bloated_color
        elif self.isObstacle:
            color = obstacle_color
        else:
            color = background_color
        return color
