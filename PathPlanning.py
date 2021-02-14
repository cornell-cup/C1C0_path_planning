from Consts import *
from grid import *


class PathPlanning:
    """
    Master file to run autonomous path planning
    Instance Attributes:
        end_point (tuple[int, int]): goal location of C1C0 in (x,y) form
        grid (Grid): grid that represents the environment
        output_state (str): string that represents the output state of C1C0
    """
    def __init__(self, end_point: tuple[int, int]):
        self.end_point: tuple[int, int] = end_point
        self.grid: Grid = Grid(tile_num_height, tile_num_width, tile_size)
        self.output_state: str = "stopped"
        # TODO: should path be a different object type?
