import grid
import math
from collections import deque
import random
import time
import Consts

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
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def euclidean_with_space(curr_pos, goal_pos, wMap):
    goal_distance = euclidean(curr_pos, goal_pos)
    index_radius_inner = int(vis_radius / tile_size)
    index_rad_outer = index_radius_inner + 2

    row = wMap._get_idx(curr_pos[1], True)
    col = wMap._get_idx(curr_pos[0], False)
    lower_row = int(max(0, row - index_rad_outer))
    lower_col = int(max(0, col - index_rad_outer))
    upper_row = int(min(row + index_rad_outer, wMap.num_rows - 1))
    upper_col = int(min(col + index_rad_outer, wMap.num_cols - 1))
    closest_obs_dist = float('inf')

    for i in range(lower_row, upper_row):
        for j in range(lower_col, upper_col):
            if i == row and j == col:
                continue
            curr_tile = wMap.grid[j][i]
            x_dist = abs(i - row)
            y_dist = abs(j - col)
            if curr_tile.isObstacle:
                closest_obs_dist = min(
                    math.sqrt(x_dist * x_dist + y_dist * y_dist),
                    closest_obs_dist)

    return goal_distance + (1 / closest_obs_dist) * alpha


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
    if (start_tile.isObstacle == True):
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
                heuristic_estimate = heuristic((neighbor.x, neighbor.y), goal,
                                               worldMap)
                # assume C1C0 moves 4 directionally and to the center of each tile
                frontier.push(neighbor, new_cost, heuristic_estimate)
                parent[neighbor] = curr
            else:
                prev_cost = frontier.getCost(neighbor)
                if new_cost < prev_cost:
                    frontier.updatePriority(neighbor, new_cost)
                    parent[neighbor] = curr

    raise NoPathError("A* failed to find a solution")


def segment_path(wMap, tiles, sample_rate=0.2):
    """
    Breaks up path of tile object [tiles] into straight line segments. Samples 
    points every [sample_rate] * [wMap].tileLength distance on potential line 
    segments to check for collisions.
    Assumes: [tiles] is a list of tiles objects returned from [a_star_search]
    on Grid object [wMap]
    [sample_rate] is a float
    """
    if len(tiles) <= 2:
        return tiles

    check_point = (tiles[-1].x, tiles[-1].y)
    curr_idx = -2
    path = [tiles[-1]]
    while curr_idx > -len(tiles):
        next_pos = (tiles[curr_idx - 1].x, tiles[curr_idx - 1].y)
        # If can't join line segment from check_point to next_pos
        if not Walkable(wMap, sample_rate, check_point, next_pos):
            path.append(tiles[curr_idx])
            check_point = (tiles[curr_idx].x, tiles[curr_idx].y)

        curr_idx -= 1

    if tiles[0] not in path:
        path.append(tiles[0])
    return path


def segment_path_dynamic(wMap, path, sample_rate=0.2):
    """Breaks up a path into a list of sub paths that are straight

    Args:
        wMap ([type]): [description]
        tiles ([type]): [description]
        sample_rate (float, optional): [description]. Defaults to 0.2.
    """


def segment_path_dyanmic(wMap, tiles, sample_rate=0.2):
    """
    calls segment path, 
    returns a list of the tiles needed to visit in straight lines 
    Also returns the tiles needed to visit to make it to the points that need to be visited
    tiles is a list of the tiles needed to be visited where every element tile[n] is a list 
    of the tiles needed to travel through to visit the nth tile in the smoothed path
    """
    if len(tiles) <= 2:
        return tiles

    check_point = (tiles[-1].x, tiles[-1].y)
    curr_idx = -2

    roughPathIndex = 0
    ##currTiles represents the tiles needed to get to the tile
    ##located at tilepath[tilepathIndex]
    currTiles = [tiles[-2]]
    roughPath = []
    roughPath.append(currTiles)

    ##The
    smoothPath = [tiles[-1]]
    currTiles = []

    while curr_idx > -len(tiles):
        next_pos = (tiles[curr_idx - 1].x, tiles[curr_idx - 1].y)

        ##add the tile to the current tiles that will be added to the rough path
        currTiles.append(tiles[curr_idx - 1])

        # If can't join line segment from check_point to next_pos
        if not Walkable(wMap, sample_rate, check_point, next_pos):
            smoothPath.append(tiles[curr_idx])
            check_point = (tiles[curr_idx].x, tiles[curr_idx].y)

            roughPath.append(currTiles)
            currTiles = []

        curr_idx -= 1

    if tiles[0] not in smoothPath:
        smoothPath.append(tiles[0])
    return smoothPath, roughPath


def Walkable(wMap, sample_rate, start_point, end_point):
    """
    Helper function for [segment_path]. Returns True if a straight line drawn
    from [start_point] to [end_point] on Grid [wMap] has no collisions with
    obstacles on [wMap] (samples points every [sample_rate] * [wMap].tileLength
    distance to check for collisions), else returns [False]. 

    Assumes: [start_point] and [end_point] are float tuples, [wMap] is a grid object
    and [sample_rate] is a float in range [0,1]
    """
    ds = sample_rate * wMap.tileLength

    rise = (end_point[1] - start_point[1])
    run = (end_point[0] - start_point[0])
    theta = math.atan2(rise, run)

    dx = ds * math.cos(theta)
    dy = ds * math.sin(theta)
    x = start_point[0]
    y = start_point[1]
    # print('theta: {}, ds: {}, dx: {}, dy: {}'.format(theta, ds, dx, dy))
    total_dist = math.sqrt(run ** 2 + rise ** 2)
    dist_travelled = 0
    while dist_travelled < total_dist:
        tile = wMap.get_tile((x, y))
        if not tile:
            print('({}, {}) OUT OF BOUNDS'.format(x, y))
            break
        elif tile.isObstacle:
            return False
        dist_travelled += math.sqrt(dx ** 2 + dy ** 2)
        x += dx
        y += dy

    return True
