from Consts import *


class Tile:
    top_terabee, mid_terabee, bottom_terabee, lidar = 0, 1, 2, 3

    def __init__(self, x, y, row, col, isObstacle = False, isBloated = False, isKnown=False):
        """
        Initialize a tile centered at x coordinate [x] and y coordinate [y].
        If [isObstacle] is True, the tile is initialized as an obstacle, else Tile is
        marked as free space, [isObstacle] is False by default.
        """
        self.obstacle_score = [0, 0, 0, 0]
        self.bloat_score = 0
        self.bloat_tiles = []
        self.is_found = False
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.is_obstacle = isObstacle
        self.is_bloated = isBloated

    def increase_score(self, sensor_type):
        """
        increase the score at that sensor type, up to a certain bound (maximal score)
        If this score fits certain conditions, then update the is_obstacle boolean accordingly
        """
        self.obstacle_score[sensor_type] = min(obstacle_threshold, self.obstacle_score[sensor_type]+1)
        if self.obstacle_score[sensor_type]==obstacle_threshold:
            self.is_obstacle = True

    def decrease_score(self, sensor_type):
        """
        decreases the score at that sensor type, as low as 0
        If this score fits certain conditions, then update the is_obstacle boolean accordingly
        """
        self.obstacle_score[sensor_type] = max(0, self.obstacle_score[sensor_type] - 1)
        if not any(self.obstacle_score):
            print("changed")
            self.is_obstacle = False
        

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
