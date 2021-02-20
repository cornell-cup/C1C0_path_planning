from SendData import *
import time
import SensorState


class PathPlanning:
    """
    Master file to run autonomous path planning
    Instance Attributes:
        end_point (tuple[int, int]): goal location of C1C0 in (x,y) form
        grid (Grid): grid that represents the environment
        output_state (str): string that represents the output state of C1C0
        distances List(tuple[int, int]): the list of tuples containing the x and y distances that C1CO should move
    """
    def __init__(self, end_point):
        self.end_point: tuple[int, int] = end_point
        self.grid: Grid = Grid(tile_num_height, tile_num_width, tile_size)
        self.output_state: str = "stopped"
        self.send_data = SendData()
        self.distances = None 
        # TODO: should path be a different object type?
    
    def path_calculation(self, map):
        startpoint = (0,0) #the position of C1C0
        path = search.a_star_search(
            emptyMap, startpoint, self.end_Point, search.euclidean)
        return search.segment_path(map, path)
        
    def dist_calc(self):
        pass
        
    
    def main_loop(self):
        """

        """
        for d in self.distances:
                self.send_data.send_data(d)
                time.sleep(2)


if __name__ == "__main__":
    # staticGridSimulation()
    emptyMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    fullMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates the enviroment based on the sensor data
    generator = Obstacles(fullMap, None, None)
    generator.update_env()
    simulation = PathPlanning((0,0))
    simulation.main_loop()
