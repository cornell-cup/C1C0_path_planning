import heapq
import math

# dict mapping position in IR sensor array to angular position on C1C0 (relative to front)
ir_mappings = {}

# C1C0 radius
radius = 0.0


class Tile:
    """
    Initialize a tile centered at x coordinate [x] and y coordinate [y]. 
    If [isObstacle] is True, the tile is initialized as an obstacle, else Tile is 
    marked as free space, [isObstacle] is False by default.
    """

    def __init__(self, x, y, isObstacle=False):
        self.x = x
        self.y = y
        self.isObstacle = isObstacle
        self.G = None
        self.H = None


class Grid:
    """
    Initialize a grid of tiles with [num_rows] rows and [num_cols] cols, with 
    each tile having length [tile_length]. The origin of the grid is the top left
    corner, with +x pointing to the right and +y pointing down.
    """

    def __init__(self, num_rows, num_cols, tile_length):
        self.grid = [[Tile((tile_length/2) + (x * tile_length), (tile_length/2) + (y * tile_length))
                      for x in range(num_cols)] for y in range(num_rows)]
        self.tileLength = tile_length

    """
    Marks tiles of grid as occuppied using IR sensor data [sensorData] measured
    from x position [x] and y position [y].
    """

    def updateGrid(self, x, y, sensorData):
        for i in range(len(sensorData)):
            angle = ir_mappings[i]
            distance = sensorData[i]
            x_obst = x + distance * math.cos(angle)
            y_obst = y - distance * math.sin(angle)
            tile_x = x_obst - (self.tileLength/2)
            tile_y = y_obst - (self.tileLength/2)
            col = self._get_idx(tile_x)
            row = self._get_idx(tile_y)
            if row > len(self.grid) or col > len(self.grid[0]):
                # TODO handle offgrid case
                return

            self.grid[row][col].isObstacle = True
            self._bloat_tile(row, col, radius)

    """
    Bloats tile at index [row][col] in grid using radius [radius].
    """
    def _bloat_tile(row, col, radius):
        # TODO obstacle bloating
        pass

    """
    Gets index of tile in grid accoding to coordinate [coord].
    """

    def _get_idx(self, coord):
        if coord < (-self.tileLength/2):
            # TODO handle off grid case
            return

        elif (-self.tileLength/2) < coord < 0:
            return 0

        else:
            low_estimate = coord//self.tileLength
            offset = coord % self.tileLength
            return low_estimate + 1 if offset > (self.tileLength/2) else low_estimate
