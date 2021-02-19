from typing import Dict
from ReceiveData import *
from grid import *

class ClientGUI:
    """
    Master file to run autonomous path planning
    Instance Attributes:
        master (Tk): Tkinter GUI object
        canvas (Canvas): Tkinter Canvas that represents the GUI
        tile_dict (Dict[Tile, Rectangle]): Mapping from tiles to rectangles on GUI
        grid (Grid): grid that represents the environment
        heading (int): integer to represent the angle that the robot is facing
    """
    def __init__(self):
        self.master: Tk = Tk()
        self.canvas: Canvas = None
        self.tile_dict: Dict[Tile, int] = None
        self.grid: Grid = Grid(tile_num_height, tile_num_width, tile_size)
        self.heading: int = 0

        self.create_widgets()
        self.receiver = ReceiveData(self.grid.grid, self.canvas, self.tile_dict)
        self.main_loop()
        self.master.mainloop()

    def create_widgets(self):
        """
        Creates the canvas of the size of the inputted grid
        """
        self.master.geometry("+900+100")
        canvas = Canvas(self.master, width=len(self.grid.grid[0]) * GUI_tile_size, height=len(self.grid.grid) * GUI_tile_size)
        offset = GUI_tile_size / 2
        tile_dict = {}
        for row in self.grid.grid:
            for tile in row:
                x = tile.x / tile_scale_fac
                y = tile.y / tile_scale_fac
                tile_dict[tile] = canvas.create_rectangle(
                    x - offset, y - offset, x + offset, y + offset, outline=tile.get_color(), fill=tile.get_color())
        canvas.pack()
        self.canvas = canvas
        self.tile_dict = tile_dict

    def main_loop(self):
        """
        """
        self.receiver.grid_update()
        self.master.after(1, self.main_loop)


if __name__ == "__main__":
    # staticGridSimulation()
    ClientGUI()

