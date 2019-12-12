import heapq


class Node:
    def __init__(self, x: int, y: int, G: int, H: int, object: bool, parent):
        self.x = x
        self.y = y
        self.G = None
        self.H = None
        self.object = object
        self.parent = None

    def __lt__(self, other):
        return self.G + self.H < other.G + other.H


def create_grid(r: int, c: int):
    grid = [[Node(x, y, None, None, False, None) for y in range(c)] for x in range(r)]
    return grid


def square(x: int):
    return x * x


def euclidean_distance(current_node: Node, end: Node):
    return (square(current_node.x - end.x) + square(current_node.y - end.y))


def search(grid, start: Node, end: Node):
    r = len(grid)
    c = len(grid[0])
    open = []
    closed = set()

    start.G = 0
    start.H = euclidean_distance(start, end)
    heapq.heappush(open, start)

    while(len(open) != 0):
        current_node = heapq.heappop(open)
        if current_node.object:
            continue
        closed.add(current_node)
        x = current_node.x
        y = current_node.y
        x_coords = [x, x, x - 1, x + 1]
        y_coords = [y - 1, y + 1, y, y]
        next_nodes = []
        for i in range(0, 4, 1):
            x_next = x_coords[i]
            y_next = y_coords[i]
            if(0 <= x_next < r and 0 <= y_next < c):
                next = grid[x_next][y_next]
                next_nodes.append(next)
        for next in next_nodes:
            if(next == end):
                next.parent = current_node
                next.G = current_node.G + 1
                return next.G
            if(next in closed or next.object):
                continue
            if(next not in open):
                next.parent = current_node
                next.G = current_node.G + 1
                next.H = euclidean_distance(next, end)
                heapq.heappush(open, next)
            else:
                if(next.G is None or current_node.G + 1 < next.G):
                    next.parent = current_node
                    next.G = current_node.G + 1
                    next.H = euclidean_distance(next, end)
                    heapq.heapify(open)
    return -1


grid = create_grid(5,5)
grid[1][0].object = True
grid[1][1].object = True
result = search(grid, grid[0][0], grid[2][0])
print(result)
current_node = grid[2][0]
while current_node is not None:
    print(str(current_node.x) + ' ' + str(current_node.y))
    current_node = current_node.parent

rows, cols = (5, 5)
#arr = [[0 for i in range(cols)] for j in range(rows)]
