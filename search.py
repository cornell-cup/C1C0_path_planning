import grid
import math
from collections import deque
import random

vis_radius = 60
tile_size = 4
# weight given to free space in [euclidean_with_space]
alpha = 2.5


class NoPathError(Exception):
    """
    Error raised when A* fails to find a solution
    """
    pass


# def euclidean(point1, point2):
#     """
#     returns a float of the euclidean distance between [point1] and [point2].

#     assumes: [point1] and [point2] are tuples with the 1st entry representing the
#     x coordinate and the 2nd representing the y coordinate
#     """
#     return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def euclidean(*argv):
    point1 = argv[0]
    point2 = argv[1]
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def euclidean_with_space(curr_pos, goal_pos, wMap):
    goal_distance = euclidean(curr_pos, goal_pos)
    index_radius_inner = int(vis_radius/tile_size)
    index_rad_outer = index_radius_inner + 2

    row = wMap._get_idx(curr_pos[1], True)
    col = wMap._get_idx(curr_pos[0], False)
    lower_row = int(max(0, row-index_rad_outer))
    lower_col = int(max(0, col-index_rad_outer))
    upper_row = int(min(row+index_rad_outer, wMap.num_rows-1))
    upper_col = int(min(col+index_rad_outer, wMap.num_cols-1))
    closest_obs_dist = float('inf')

    for i in range(lower_row, upper_row):
        for j in range(lower_col, upper_col):
            if i == row and j == col:
                continue
            curr_tile = wMap.grid[j][i]
            x_dist = abs(i-row)
            y_dist = abs(j-col)
            if curr_tile.isObstacle:
                closest_obs_dist = min(
                    math.sqrt(x_dist*x_dist+y_dist*y_dist), closest_obs_dist)

    return goal_distance + (1/closest_obs_dist) * alpha


def a_star_search(worldMap, start, goal, heuristic):
    """
    Calculates a path through grid [worldMap] from (x,y) coordinates [start] to
    (x,y) coordinates [goal] using A* search with heuristic function [heuristic]. 
    Returns a tuple of the deque of tuples where each entry represents the x and y distance to 
    get to the next tile, and a set of the tiles that were visited along the path. 
    Returns None if there is no valid path from [start] to [goal].

    assumes: [heuristic] is a function that takes in the current position, goal position
    and a grid object and outputs a float. Current position and goal position are
    float tuples
    """

    start_tile = worldMap.get_tile(start)
    goal_tile = worldMap.get_tile(goal)
    ##############CODE TO ENSURE START TILE CAN'T BE OBSTACLE##################
    if(start_tile.isObstacle == True):
        start_tile.isObstacle = False

    ##############CODE TO ENSURE END TILE CAN'T BE OBSTACLE##################
    if start_tile is None or goal_tile is None:
        start_tile.isObstacle = False

    frontier = grid.TileHeap()
    frontier.push(start_tile, 0, heuristic(start, goal, worldMap))
    closed = set()
    parent = {}
    path_dist = deque()
    path_tiles = []

    while not frontier.isEmpty():
        curr, curr_cost = frontier.pop()
        if curr == goal_tile:
            # assumes won't have trivial case of start == goal
            while curr != start_tile:
                prev = parent[curr]
                if prev != start_tile:
                    x_dist = curr.x - prev.x
                    y_dist = curr.y - prev.y
                else:
                    x_dist = curr.x - start[0]
                    y_dist = curr.y - start[1]

                path_dist.appendleft((x_dist, y_dist))
                path_tiles.append(curr)
                curr = prev

            path_tiles.append(start_tile)
            return (path_dist, path_tiles)

        closed.add(curr)
        neighbors = worldMap.get_neighbors(curr)
        for neighbor in neighbors:
            if neighbor in closed:
                continue

            # 1st move is special case since start position doesn't have to be at the center of a tile
            if curr == start_tile:
                new_cost = euclidean(start, (neighbor.x, neighbor.y))
            else:
                new_cost = curr_cost + worldMap.tileLength

            if not frontier.mem(neighbor):
                heuristic_estimate = heuristic(
                    (neighbor.x, neighbor.y), goal, worldMap)
                # assume C1C0 moves 4 directionally and to the center of each tile
                frontier.push(neighbor, new_cost, heuristic_estimate)
                parent[neighbor] = curr
            else:
                prev_cost = frontier.getCost(neighbor)
                if new_cost < prev_cost:
                    frontier.updatePriority(neighbor, new_cost)
                    parent[neighbor] = curr

    raise NoPathError("A* failed to find a solution")


# wMap = grid.Grid(300, 300, 3)
# for row in range(len(wMap.grid)):
#     for col in range(len(wMap.grid[0])):
#         if (row + col == 0) or (row + col == len(wMap.grid) + len(wMap.grid[0]) - 2):
#             continue
#         rint = random.randint(0, 3)
#         if not rint:
#             wMap.grid[row][col].isObstacle = True

# dist, tiles = a_star_search(wMap, (2.0, 2.0), (898.0, 898.0), euclidean)
# print([(tile.x, tile.y) for tile in tiles])
