import grid
import math
import gui
from collections import deque

"""
returns a float of the euclidean distance between [point1] and [point2].

assumes: [point1] and [point2] are tuples with the 1st entry representing the 
x coordinate and the 2nd representing the y coordinate
"""


def euclidean(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


"""
Calculates a path through grid [worldMap] from (x,y) coordinates [start] to
(x,y) coordinates [goal] using A* search with heuristic function [heuristic]. 
Returns a tuple of the deque of tuples where each entry represents the x and y distance to 
get to the next tile, and a set of the tiles that were visited along the path. 
Returns None if there is no valid path from [start] to [goal].

assumes: [heuristic] is a function that takes in two float tuples and outputs a 
float
"""


def a_star_search(worldMap, start, goal, heuristic):
    start_tile = worldMap.get_tile(start)
    goal_tile = worldMap.get_tile(goal)

    if start_tile is None or goal_tile is None:
        return

    frontier = grid.TileHeap()
    frontier.push(start_tile, 0, heuristic(start, goal))
    closed = set()
    parent = {}
    path_dist = deque()
    path_tiles = set()

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
                path_tiles.add(curr)
                curr = prev

            path_tiles.add(start_tile)
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
                heuristic_estimate = heuristic((neighbor.x, neighbor.y), goal)
                # assume C1C0 moves 4 directionally and to the center of each tile
                frontier.push(neighbor, new_cost, heuristic_estimate)
                parent[neighbor] = curr
            else:
                prev_cost = frontier.getCost(neighbor)
                if new_cost < prev_cost:
                    frontier.updatePriority(neighbor, new_cost)
                    parent[neighbor] = curr

    return


if __name__ == "__main__":
    wMap = grid.Grid(5, 5, 40)
    wMap.grid[1][1].isObstacle = True
    wMap.grid[1][2].isObstacle = True
    wMap.grid[1][3].isObstacle = True
    wMap.grid[1][4].isObstacle = True
    wMap.grid[3][0].isObstacle = True
    wMap.grid[3][1].isObstacle = True
    wMap.grid[3][2].isObstacle = True
    wMap.grid[3][3].isObstacle = True
    dists, tiles = a_star_search(wMap, (20.0, 180.0), (180.0, 20.0), euclidean)
    gui.searchGUI(wMap, tiles)
