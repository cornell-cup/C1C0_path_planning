import heapq
import math

# dict mapping position in IR sensor array to angular position on C1C0 (relative to front)
ir_mappings_top = {}
ir_mappings_bot = {}

# C1C0 radius
radius = 0.0


class Tile:
    """
    Initialize a tile centered at x coordinate [x] and y coordinate [y]. 
    If [isObstacle] is True, the tile is initialized as an obstacle, else Tile is 
    marked as free space, [isObstacle] is False by default.
    """

    def __init__(self, x, y, isObstacle=False):

        self.y = y
        self.isObstacle = isObstacle
        self.G = None  # cost info for A* search
        self.H = None  # heuristic info for A* search
        self.parent = None  # info for constructing path from search


class TileHeap:
    """
    """

    def __init__(self):
        self.data = []
        self.cost_map = {}
        self.idx_map = {}

    """
    """

    def comparator(self, pos1, pos2):
        tile1 = self.data[pos1]
        tile2 = self.data[pos2]
        data1 = self.cost_map[tile1][0] + self.cost_map[tile1][1]
        data2 = self.cost_map[tile2][0] + self.cost_map[tile2][1]
        if data1 == data2:
            return 0
        elif data1 < data2:
            return -1
        else:
            return 1

    """
    Push [elt] on to the heap
    """

    def push(self, elt, cost, heuristic):
        if elt in self.idx_map:
            return None

        pos = len(self.data)
        self.idx_map[elt] = pos
        self.cost_map[elt] = [cost, heuristic]
        self.data.append(elt)
        self._bubble_up(pos)

    """
    Pop item from heap, raises IndexError if heap is empty 
    """

    def pop(self):
        if len(self.data) == 1:
            elt = self.data.pop()
            del self.idx_map[elt]
            del self.cost_map[elt]
            return elt

        elt = self.data[0]
        del self.idx_map[elt]
        del self.cost_map[elt]
        last = self.data.pop()
        self.data[0] = last
        self.idx_map[last] = 0
        self._bubble_down()
        return elt

    """
    """

    def _swap(self, pos1, pos2):
        elt1 = self.data[pos1]
        elt2 = self.data[pos2]
        self.idx_map[elt1], self.idx_map[elt2] = self.idx_map[elt2], self.idx_map[elt1]
        self.data[pos1], self.data[pos2] = elt2, elt1

    """
    """

    def _bubble_up(self, pos):
        parent = (pos - 1)//2
        while pos > 0 and self.comparator(pos, parent) > 0:
            self._swap(pos, parent)
            pos = parent
            parent = (pos - 1)//2

    """
    """

    def _biggerChild(self, pos):
        c = 2*pos + 2
        if c >= len(self.data) or self.comparator(c-1, c) > 0:
            c = c-1
        return c

    """
    """

    def _bubble_down(self, pos):
        child = self._biggerChild(pos)
        while (child < len(self.data) and self.comparator(pos, child) < 0):
            self._swap(pos, child)
            pos = child
            child = self._biggerChild(pos)

    """
    """

    def updatePriority(self, elt, new_cost):
        self.cost_map[elt][0] = new_cost
        pos = self.idx_map[elt]
        self._bubble_up(pos)
        self._bubble_down(pos)

    """
    Returns True if heap is empty, else returns False
    """

    def isEmpty(self):
        return False if self._data else False


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
        # TODO change center pos

    """
    Marks tiles of grid as occuppied using IR sensor data [sensorData] measured
    from x position [x] and y position [y].
    """

    def updateGrid(self, x, y, sensorDataTop, sensorDataBot):
        for i in range(len(sensorDataTop)):
            angle = ir_mappings_top[i]
            distance = sensorDataTop[i]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                y_obst = y + radius - distance * math.sin(angle)
                col = self._get_idx(x_obst)
                row = self._get_idx(y_obst)
                if row > len(self.grid) or col > len(self.grid[0]):
                    # TODO handle offgrid case
                    return
                self.grid[row][col].isObstacle = True
                self._bloat_tile(row, col, radius)

        for i in range(len(sensorDataBot)):
            angle = ir_mappings_bot[i]
            distance = sensorDataBot[i]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                y_obst = y + radius - distance * math.sin(angle)
                col = self._get_idx(x_obst)
                row = self._get_idx(y_obst)
                if row > len(self.grid) or col > len(self.grid[0]):
                    # TODO handle offgrid case
                    return
                self.grid[row][col].isObstacle = True
                self._bloat_tile(row, col, radius)

    """
    Bloats tile at index [row][col] in grid using radius [radius].
    """

    def _bloat_tile(self, row, col, radius):
        # TODO obstacle bloating
        pass

    """
    Gets index of tile in grid accoding to coordinate [coord].
    """

    def _get_idx(self, coord):
        coord -= (self.tileLength/2)
        if coord < (-self.tileLength/2):
            # TODO handle off grid case
            return

        elif (-self.tileLength/2) < coord < 0:
            return 0

        else:
            low_estimate = coord//self.tileLength
            offset = coord % self.tileLength
            return low_estimate + 1 if offset > (self.tileLength/2) else low_estimate
