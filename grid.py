import heapq
import math

# dict mapping position in IR sensor array to angular position on C1C0 (relative to front)
ir_mappings = {}

# C1C0 radius
radius = 0.0


class Heap:
    """
    """

    def __init__(self, priority=lambda x: x):
        self.priority = priority
        self.data = []
        self.mappings = {}

    """
    Push [elt] on to the heap
    """

    def push(self, elt):
        if elt in self.mappings:
            return None

        pos = len(self.data)
        self.mappings[elt] = pos
        self.data.append(elt)
        self._bubble_up(pos)

    """
    Pop item from heap, raises IndexError if heap is empty 
    """

    def pop(self):
        if len(self.data) == 1:
            elt = self.data.pop()
            del self.mappings[elt]
            return elt

        elt = self.data[0]
        del self.mappings[elt]
        last = self.data.pop()
        self.data[0] = last
        self.mappings[last] = 0
        self._bubble_down()
        return elt

    """
    """

    def _bubble_up(self, pos):
        # TODO implement
        pass

    """
    """

    def _bubble_down(self, pos):
        # TODO implement
        pass

    """
    Returns True if heap is empty, else returns False
    """

    def isEmpty(self):
        return False if self._data else False


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
        self.G = None  # cost info for A* search
        self.H = None  # heuristic info for A* search
        self.parent = None  # info for constructing path from search


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

    """
    """

    def search(self, start, end, heuristic):
        x_0, y_0 = start[0], start[1]
        x_end, y_end = end[0], end[1]

        # TODO handle out of bounds case
        start_tile = self.grid[self._get_idx(y_0)][self._get_idx(x_0)]
        end_tile = self.grid[self._get_idx(y_end)][self._get_idx(x_end)]

        #open = HeapWrapper(key = lambda tile: tile.H + tile.G)
        closed = set()

        start_tile.G = 0
        start_tile.H = heuristic(start, end)
        open.push(start_tile)

        while not open.isEmpty():
            curr = open.pop()
            if curr.isObstacle:
                continue
            closed.add(curr)
