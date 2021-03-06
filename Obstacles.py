import grid
from Consts import *
import SensorState

class Obstalces():
    def __init__(self, grid, canvas, sensor_data):
        """A class to help generate the environment from the sensor data

        Arguments:
            grid {grid.grid} -- The grid to fill in with obstacles

        FIELDS:
        gridObj {Grid} -- Grid object to generate on 
        grid {list (list Tile)} -- the actual grid of tiles
        canvas {Canvas} -- the canvas the GUI is made on
        sensor_data{List[tuple[int, int]]} -- list of tuples containing the (x,y) position of obstacles
        height {int} -- height of grid
        width {int} -- width of grid
        """
        self.gridObj = grid
        self.grid = grid.grid
        self.sensor_data = sensor_data
        self.canvas: Canvas = canvas
        
    def update_env(self):
        for obst in self.sensor_data:
            row = obst[0]
            col = obst[1]
            self.grid[row][col].is_obstacle = True
            self.canvas.itemconfig(
                self.grid[row][col], outline=obstacle_color, fill=obstacle_color)