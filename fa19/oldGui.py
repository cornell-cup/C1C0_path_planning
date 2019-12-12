from tkinter import *;
from A_Star_Search import *;

def main():
    rows, cols = (5, 5)
    arr = [[0 for i in range(cols)] for j in range(rows)]

    grid = create_grid(5,5)
    grid[1][0].object = True
    grid[1][1].object = True
    result = search(grid, grid[0][0], grid[2][0])
    #print(result)
    current_node = grid[2][0]
    while current_node is not None:
        #print(str(current_node.x) + ' ' + str(current_node.y))
        arr[current_node.x][current_node.y] = 6;
        current_node = current_node.parent

    print(arr)

    Map = [
            [2, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 1, 3, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
          ]
    root = Tk()
    root.resizable(True, True);
    my_gui = CellGrid(root, len(Map), len(Map[0]), 40, Map)
    root.mainloop()

class CellGrid(Canvas):
    def __init__(self,master, rowNumber, columnNumber, cellSize, theMap):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber)

        self.cellSize = cellSize

        self.pack(expand=True);

        self.grid = []
        for row in range(rowNumber):
            line = []
            for column in range(columnNumber):
                line.append(Cell(self, column, row, cellSize, theMap[row][column]))
            self.grid.append(line)

        #print(self.grid[0][0].value)
        self.draw()


    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

class Cell():
    START_COLOR = "green"
    FINISH_COLOR = "red"
    UNTRIED_COLOR = "white"
    CLOSED_COLOR = "gray"
    OPEN_COLOR = "blue"
    OBSTACLE_COLOR = "black"
    PATH_COLOR = "orange"

    def __init__(self, master, x, y, size, value):
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill = "white"
        self.value = value

    def setValue(self, value):
        self.value = value

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None :
            if self.value == 0:
                self.fill = self.UNTRIED_COLOR
            elif self.value == 1:
                self.fill = self.OBSTACLE_COLOR
            elif self.value == 2:
                self.fill = self.START_COLOR
            elif self.value == 3:
                self.fill = self.FINISH_COLOR
            elif self.value == 4:
                self.fill = self.OPEN_COLOR
            elif self.value == 5:
                self.fill = self.CLOSED_COLOR
            elif self.value == 6:
                self.fill = self.PATH_COLOR

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill = self.fill, outline = "black")

main();
