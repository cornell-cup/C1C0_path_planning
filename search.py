import grid
import math


def euclidean(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def search(grid, start, goal):
    start_tile = grid.get_tile(start)
    goal_tile = grid.get_tile(goal)

    if start_tile is None or goal_tile is None:
        return

    frontier = grid.TileHeap()
    frontier.push(start_tile, 0, euclidean(start, goal))
    closed = set()
    path = []

    while not frontier.isEmpty():
        curr = frontier.pop()
        if curr == goal_tile:
            path.append((curr.x, curr.y))
            return path

        neighbors = grid.get_neighbors(curr)
