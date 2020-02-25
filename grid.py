import heapq
import math

# dict mapping position in IR sensor array to angular position on C1C0 (relative to front)
ir_mappings_top = {}
ir_mappings_bot = {}

# C1C0 radius
radius = 0.0

# How many radius' of C1C0 we should use
bloatFactor = 2


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


class TileHeap:
    """
    Initializes an empty heap of tiles.
    """

    def __init__(self):
        self.data = []
        self.cost_map = {}  # to keep track of each tiles cost + heuristic
        self.idx_map = {}  # to keep track of each tiles index in data

    """
    given index [pos1] and index [pos2] of the heap, returns 0 if tile at 
    [pos1] has same cost + heuristic as the tile at [pos2]; returns -1 if 
    tile at [pos1] has greater cost + heuristic than tile at [pos2] and returns
    1 if tile at [pos1] has smaller cost + heuristic than tile at [pos2].
    """

    def comparator(self, pos1, pos2):
        tile1 = self.data[pos1]
        tile2 = self.data[pos2]
        data1 = self.cost_map[tile1][0] + self.cost_map[tile1][1]
        data2 = self.cost_map[tile2][0] + self.cost_map[tile2][1]
        if data1 == data2:
            return 0
        elif data1 > data2:
            return -1
        else:
            return 1

    """
    Push tile [elt] on to the heap with cost [cost] and heuristic estimate 
    [heuristic]

    assumes: [elt] is a Tile object, [cost] and [heuristic] are floats
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
    Pop tile with minimum cost + heuristic from heap and return a tuple of tile
    and cost to get to the tile (in that order), returns None if heap is empty.
    """

    def pop(self):
        if self.isEmpty():
            return None

        elt = self.data[0]
        cost = self.cost_map[elt][0]
        del self.idx_map[elt]
        del self.cost_map[elt]
        if len(self.data) > 1:
            last = self.data.pop()
            self.data[0] = last
            self.idx_map[last] = 0
            self._bubble_down(0)

        return (elt, cost)

    """
    swap tile at [pos1] in heap with tile at [pos2] in heap.
    """

    def _swap(self, pos1, pos2):
        elt1 = self.data[pos1]
        elt2 = self.data[pos2]
        self.idx_map[elt1], self.idx_map[elt2] = pos2, pos1
        self.data[pos1], self.data[pos2] = elt2, elt1

    """
    helper function for [push] and [updatePriority]
    """

    def _bubble_up(self, pos):
        parent = (pos - 1)//2
        while pos > 0 and self.comparator(pos, parent) > 0:
            self._swap(pos, parent)
            pos = parent
            parent = (pos - 1)//2

    """
    helper function for [pop], returns the child of element at [pos] with the
    highest priority
    """

    def _biggerChild(self, pos):
        c = 2*pos + 2
        if c >= len(self.data) or self.comparator(c-1, c) > 0:
            c = c-1
        return c

    """
    helper function for [pop] and [updatePriority]
    """

    def _bubble_down(self, pos):
        child = self._biggerChild(pos)
        while (child < len(self.data) and self.comparator(pos, child) < 0):
            self._swap(pos, child)
            pos = child
            child = self._biggerChild(pos)

    """
    updates tile [elt] in the heap with cost [new_cost].
    Assumes [elt] is already in the heap

    Note: [new_cost] should not include heuristic estimate
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
        return False if self.data else True

    """
    returns True if [elt] is in the heap, else returns False
    """

    def mem(self, elt):
        return elt in self.idx_map

    """
    Returns the cost from start to tile [elt] if [elt] is in heap, else returns
    None
    """

    def getCost(self, elt):
        if not self.mem(elt):
            return
        return self.cost_map[elt][0]


class Grid:
    """
    Initialize a grid of tiles with [num_rows] rows and [num_cols] cols, with 
    each tile having length [tile_length]. The origin of the grid is the top left
    corner, with +x pointing to the right and +y pointing down.

    assumes: [num_rows] is even
    """

    def __init__(self, num_rows, num_cols, tile_length):
        self.grid = [[Tile((tile_length/2) + (x * tile_length), (tile_length/2) + (y * tile_length))
                      for x in range(num_cols)] for y in range(num_rows-1, 0, -1)]
        self.tileLength = tile_length
        # TODO change center pos

    """
    Marks tiles of grid as occuppied using IR sensor data [sensorData] measured
    from x position [x] and y position [y].
    """

    def updateGrid(self, x, y, sensorDataTop, sensorDataBot, path):
        # returner is a variable to keep track of whether
        # A-star needs to be re-run
        returner = False
        for i in range(len(sensorDataTop)):
            angle = ir_mappings_top[i]
            distance = sensorDataTop[i]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                y_obst = y + radius + distance * math.sin(angle)
                col = self._get_idx(x_obst, False)
                row = self._get_idx(y_obst, True)
                if row > len(self.grid) or col > len(self.grid[0]):
                    # TODO handle offgrid case
                    return
                if(self.grid[row][col] in path):
                    returner = True
                self.grid[row][col].isObstacle = True
                if(self._bloat_tile(row, col, path) == True):
                    returner = True

        for i in range(len(sensorDataBot)):
            angle = ir_mappings_bot[i]
            distance = sensorDataBot[i]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                y_obst = y + radius + distance * math.sin(angle)
                col = self._get_idx(x_obst, False)
                row = self._get_idx(y_obst, True)
                if row > len(self.grid) or col > len(self.grid[0]):
                    # TODO handle offgrid case
                    return
                if(self.grid[row][col] in path):
                    returner = True
                self.grid[row][col].isObstacle = True
                if(self._bloat_tile(row, col, radius) == True):
                    returner = True

        return returner

    """
    Bloats tile at index [row][col] in grid using radius [radius].
    Going off grid, could final tile get bloated?
    TODO
    """

    def _bloat_tile(self, row, col, path):
        # TODO obstacle bloating
        returner = False
        xCenter = self.grid[row][col].x
        yCenter = self.grid[row][col].y
        bloatedRadius = radius * bloatFactor

        return returner

    """
    Gets index of tile in grid accoding to coordinate [coord]. [coord] is assumed
    to be a y coordinate if [is_y] is True, else [coord] is assumed to be an x coordinate
    returns None if coord isn't on the grid.
    """

    def _get_idx(self, coord, is_y):
        if is_y:
            if coord < 0 or coord > len(self.grid) * self.tileLength:
                # TODO handle off grid case
                return
        else:
            if coord < 0 or coord > len(self.grid[0]) * self.tileLength:
                # TODO handle off grid case
                return

        coord -= (self.tileLength/2)
        if (-self.tileLength/2) < coord < 0:
            return 0

        else:
            low_estimate = int(coord//self.tileLength)
            offset = coord % self.tileLength
            ret = low_estimate + \
                1 if offset > (self.tileLength/2) else low_estimate
            if is_y:
                return (len(self.grid) - 1) - ret
            else:
                return ret

    """
    returns the tile at (x,y) coordinates [coords]. If [coords] is outside the
    grid returns None
    """

    def get_tile(self, coords):
        col = self._get_idx(coords[0], False)
        row = self._get_idx(coords[1], True)
        if col is None or row is None:
            return

        return self.grid[row][col]

    """
    Returns a list of the free tiles neighboring [tile] in grid
    """

    def get_neighbors(self, tile):
        col = self._get_idx(tile.x, False)
        row = self._get_idx(tile.y, True)
        res = []
        if col is None or row is None:
            return res

        options = [(col-1, row), (col+1, row), (col, row+1), (col, row-1)]
        for icol, irow in options:
            if not (0 <= icol < len(self.grid[0])) or not(0 <= irow < len(self.grid)):
                continue
            if self.grid[irow][icol].isObstacle:
                continue
            res.append(self.grid[irow][icol])

        return res
