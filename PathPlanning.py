from SendData import *
import time


class PathPlanning:
    """
    Master file to run autonomous path planning
    Instance Attributes:
        end_point (tuple[int, int]): goal location of C1C0 in (x,y) form
        grid (Grid): grid that represents the environment
        output_state (str): string that represents the output state of C1C0
    """
    def __init__(self, end_point):
        self.end_point: tuple[int, int] = end_point
        self.grid: Grid = Grid(tile_num_height, tile_num_width, tile_size)
        self.output_state: str = "stopped"
        self.send_data = SendData()
        # TODO: should path be a different object type?

    def main_loop(self):
        """

        """
        for i in range(len(self.grid.grid)):
            for j in range(len(self.grid.grid[i])):
                self.grid.grid[i][j].is_obstacle = True
                print('sending data')
                self.send_data.send_data(self.grid.grid)
                print('data sent')
                time.sleep(2)


if __name__ == "__main__":
    # staticGridSimulation()
    simulation = PathPlanning((0,0))
    simulation.main_loop()
