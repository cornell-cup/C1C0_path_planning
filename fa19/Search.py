

class Heap:
    def __init__(self, comparator = None):
        self.heap = [] # list of (comparator(element), element) tuples
        self.mappings = {} # elts -> position in heap
        if not self.comparator:
            self.comparator = lambda x: x
        else:
            self.comparator = comparator

    def __element__(self, key, value):
        self.key = key
        self.value = value

    def __len__(self):
        return len(self.heap)

    def mem(self, val):
        return val in self.mappings

    def bubble_up(self):
        # TODO

    def bubble_down(self):
        # TODO
        return
    def push(self, val):
        # # TODO:

    def update_key(self, key):
        return self


class Grid:
    '''
    Constructor for Grid: Initialize a matrix with size of rows and colums. The
    matrix is a 2d array collections of Tile objects.
    '''
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.matrix = [[Tile(x, y) for y in range(columns)] for x in range(rows)]
        self.explored = []

    def manhattan_distance(self, current_tile, end_tile):
        return abs(current_tile.x - end_tile.x) + abs(current_tile.y - end_tile.y)

    # A* searching algortihm
    def a_star_search(self, graph, start, goal):

        # heap -> open set ordered on cost
        heap = Heap(lambda tile: tile.G + tile.H, [start])

        # Initialize both open_set and closed_set
        # set -> open set
        open_set = {start: 0}
        # set -> closed set
        closed_set = set()

        # add start to heap G = 0, H = estimate to goal
        start.H = self.manhattan_distance(start, goal)
        open_set.add(start)


        # while heap is not empty
            # check if top of heap is goal
            # if not, add to closed set, get empty neighbors and calculate cost and heuristic
            # if neighbor in open set check if cost is less, if it is, update cost of successor and parent tile
            # if in closed set and cost is less, put closed set node back on open set and update parent (unsure)
            while not heap.isEmpty():
                top_elt = heap.pop()
                open_set.remove(top_elt)
                closed_set.add(top_elt)

                # if the top element is goal, stop the searching algorithm
                if top_elt == goal:
                    break

                # get a list of empty neighbor tiles
                neighbors = []
                cur_x = top_elt.x
                cur_y = top_elt.y

                next_tiles = [(cur_x - 1, cur_y), (cur_x + 1, cur_y), (cur_x, cur_y - 1), (cur_x, cur_y + 1)]
                for x, y in next_tiles:
                    if(0 <= x < Grid.rows and 0 <= y < Grid.columns and Grid[x][y].isEmpty and Grid[x][y] not in closed_set):
                        neighbors.append(Grid[x][y])

                # update the cost of successor and parent tile if neighbor
                # node is in open set
                for node in neighbors:
                    if node in open_set:
                        if top_elt.G + 1 < node.G:
                            node.G = top_elt.G + 1
                            node.parent = top_elt
                    else:
                        node.G = top_elt.G + 1
                        node.H = self.manhattan_distance(node, goal)
                        node.parent = top_elt
                        open_set.add(node)
                        heap.push(node)




        # fail if get to here here

    #Returns the path as a list of (x,y) coordinates, includes the tile itself
    def get_path(tile):
        path = []
        current_tile = tile
        while(current_tile is not None):
            path.append((current_tile.x, current_tile.y))
            current_tile = current_tile.parent
        return path

class Tile:
    '''
    The class Tile carries the information of position of each tile in the matrix.
    The position is represented by x, rows, and y, columns. It also contains info
    whether the tile is empty or not with boolean value and cost of reaching specific
    that tile. The cost is initialized to be None at first and then being updated
    to integer and every tile is initialized to be empty at first.
    '''
    def __init__(self, x, y, isEmpty = True, parent = None):
        # add parent tile field
        self.x = x
        self.y = y
        self.isEmpty = isEmpty
        self.parent = parent
        self.G = 0 # distance between the start node and the current node
        self.H = 0 # heuristic — estimated distance from the current node to the end node
        # F = G + H
        # self.F = 0 # total cost of the node

a = Grid(2, 3)
for i in range(a.rows):
    for j in range(a.columns):
        print(a.matrix[i][j], end = '')
    print('.')

# driver function
if __name__ == '__main__':
    main()
