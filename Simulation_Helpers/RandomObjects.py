import math
from Constants.Consts import *

import json

from Simulation_Helpers.SquareObstacles import *


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

class RandomObjects():
    def __init__(self, grid):
        """A class to help generate a random enviroment with random objects

        Arguments:
            grid {grid.grid} -- The grid to fill in with obstacles

        FIELDS:
        gridObj {Grid} -- Grid object to generate on 
        grid {list (list Tile)} -- the actual grid of tiles
        height {int} -- height of grid
        width {int} -- width of grid
        doc {object list} -- used as an accumulator of the list of objects generated and recorded so far
        """
        self.gridObj = grid
        self.grid = grid.grid
        self.height = grid.num_rows
        self.width = grid.num_cols
        self.doc=[]
        self.squares = []

    def bloatTiles(self, radius, bloat_factor):
        """bloats the tiles in this grid
        """
        for i in range(self.height):
            for j in range(self.width):
                if (self.grid[i][j].is_obstacle == True and self.grid[i][j].is_bloated == False):
                    self.gridObj.bloat_tile(
                        i, j, radius, bloat_factor)

    def generateBox(self):
        """Generates a random box of a random size in the grid
        """
        sizeScalarW = int(math.sqrt(self.height))
        sizeScalarH = int(math.sqrt(self.height))
        sizeScalar = int(min(sizeScalarH, sizeScalarW * 1.4))
        goodLoc = False
        while not goodLoc:
            goodLoc = True
            randW = random.randint(int(sizeScalar / 6), sizeScalar)
            randH = random.randint(int(sizeScalar / 6), sizeScalar)


            randX = random.randint(0, self.width - randW)
            randY = random.randint(0, self.height - randH)
            randVelocities = [0, 2, 1, 0.5]
            randVelocity = randVelocities[random.randint(0, 3)]
            if self.width / 2 + tol > randX > self.width / 2 - tol:
                if self.height / 2 + tol > randY > self.height / 2 - tol:
                    goodLoc = False

        for y in range(randY, randY + randH):
            for x in range(randX, randX + randW):
                self.grid[y][x].is_obstacle = True
        self.squares.append(SquareObstacles(randX, randY, randH, randW, randVelocity, 0))

        # storing attributes of generated rectangle to be used to create json file from this environment later
        docdict= {}
        docdict["type"]="rectangle"
        docdict["width"]=randW
        docdict["height"]=randH
        docdict["x"]=randX
        docdict["y"]=randY
        self.doc.append(docdict)

    def generateCirc(self):
        pass

    def generateCrec(self):
        pass

    def generateBar(self):
        """generates a bar of width 1, 2 or three
        """
        goodLoc = False
        while not goodLoc:
            goodLoc = True
            barWidth = random.randint(1, 3)
            barLength = random.randint(int(self.height / 6), int(2 * self.height / 3))
            barX = random.randint(1, self.width)
            barY = random.randint(0, self.height - barLength)

            if (barX < self.width / 2 + tol and barX > self.width / 2 - tol):
                mini = max(0, barY - tol)
                maxi = min(self.height - 1, barY + barLength + tol)
                for i in range(mini, maxi):
                    if (i < self.height / 2 + tol and i > self.height / 2 - tol):
                        goodLoc = False

        randomChance = random.randint(1, 4)
        if (randomChance == 1):
            barY = 0
        elif (randomChance == 2):
            barY = self.height - barLength
        for i in range(barWidth):
            for j in range(barLength):
                if (barY + j < self.height and barX + i < self.width - 1):
                    self.grid[barY + j][barX + i].is_obstacle = True

        docdict = {}
        docdict["type"] = "rectangle"
        docdict["width"] = min(barWidth, self.width - barX)
        docdict["height"] = min(barLength, self.height - barY)
        docdict["x"] = barX
        docdict["y"] = barY
        self.doc.append(docdict)

    def generateSeq(self):
        """Calculates a random size and location to generate a randomized shape
        then calls recursiveGen() many times to generate the shape
        """
        self.doc.append({})
        self.doc[-1]['type']= 'other-dots'
        self.doc[-1]['dots']= []
        sizeScalarW = int(math.sqrt(self.width) * 1.2)
        sizeScalarH = int(math.sqrt(self.height) * 1.2)
        sizeScalar = min(sizeScalarH, sizeScalarW)
        sizeScalar = random.randint(int(sizeScalar / 4), sizeScalar)
        # robot's right most initial x position
        robot_right = self.width / 2 + robot_radius / tile_size + 1
        # robot's left most initial x position
        robot_left = self.width / 2 - robot_radius / tile_size - 1
        # robot's down most initial y position
        robot_down = self.height / 2 - robot_radius / tile_size - 1
        # robot's up most initial y position
        robot_up = self.height / 2 + robot_radius / tile_size + 1
        goodLoc = False
        #numLoops= 0
        #maxLoops= 10
        while not goodLoc:
            #numLoops+= 1
            #print(numLoops)
            randX = random.randint(0, self.width - sizeScalar)
            randY = random.randint(0, self.height - sizeScalar)
            # object's left most x position
            object_left = randX - sizeScalar - (robot_radius / tile_size) * bloat_factor
            # object's right most x position
            object_right = randX + sizeScalar + (robot_radius / tile_size) * bloat_factor
            # object's up most y position
            object_up = randY + sizeScalar + (robot_radius / tile_size) * bloat_factor
            # object's down most y position
            object_down = randY - sizeScalar - (robot_radius / tile_size) * bloat_factor

            # checks if any part of the object falls in the x bounds of the robot
            def x_conditions():
                return object_left <= robot_left <= object_right or object_left <= robot_right <= object_right \
                or (object_left <= robot_left and object_right >= robot_right)

            # checks if any part of the object falls in the y bounds of the robot
            def y_conditions():
                return object_down <= robot_down <= object_up or object_down <= robot_up <= object_up \
                or (object_down <= robot_down and object_up >= robot_up)

            if object_up >= self.height or object_right >= self.width or object_down <= 0 or object_left <= 0:
                goodLoc = False
            # checks to see if the randX and randY is not overlapping with the robot's start position in the simulation
            elif x_conditions() and y_conditions():
                goodLoc = False
            else:
                goodLoc = self.grid[randY][randX].is_obstacle == False and self.grid[randY + sizeScalar][
                    randX].is_obstacle == False and self.grid[randY][randX +
                                                                     sizeScalar].is_obstacle == False and \
                          self.grid[randY + sizeScalar][randX + sizeScalar].is_obstacle == False

        if (randX < self.width / 2 + tol and randX > self.width / 2 - tol):
            if (randY < self.height / 2 + tol and randY > self.height / 2 - tol):
                return

        for i in range(sizeScalar * 4):
            self.recursiveGen(sizeScalar, randX, randY)

    def recursiveGen(self, depth, x, y):
        """This recursive function starts at the grid located at x y,
        and then fills in tiles as obstacles randomly jumping to locations
        next to the grid depth times

        Arguments:
            depth {int} -- Home many tiles to fill in as obstacles
            x {int} -- column of grid to fill in
            y {int} -- row of grid to fill in
        """
        if (depth == 0):
            return
        randNum = random.randint(1, 4)
        if (randNum == 1):
            self.grid[y][x - 1].is_obstacle = True
            self.doc[-1]['dots'].append([y, x-1])
            self.recursiveGen(depth - 1, x - 1, y)
        if (randNum == 2):
            self.grid[y - 1][x].is_obstacle = True
            self.doc[-1]['dots'].append([y-1, x])
            self.recursiveGen(depth - 1, x, y - 1)
        if (randNum == 3):
            self.grid[y][x + 1].is_obstacle = True
            self.doc[-1]['dots'].append([y, x+1])
            self.recursiveGen(depth - 1, x + 1, y)
        if (randNum == 4):
            self.grid[y + 1][x].is_obstacle = True
            self.doc[-1]['dots'].append([y+1, x])
            self.recursiveGen(depth - 1, x, y + 1)

    def create_env(self, numBoxes, numCirc, numCrec, numSeq, numBars):
        """Generates an enviroment with many randomized obstacles of different
        shapes and sizes, each argument corresponds to how many
        of those obstacles should be generated

        Arguments:
            numBoxes {int} -- [description]
            numCirc {int} -- [description]
            numCrec {[type]} -- [description]
            numSeq {[type]} -- [description]
        """
        for i in range(numBoxes):
            self.generateBox()
        for k in range(numBars):
            self.generateBar()
        for j in range(numSeq):
            self.generateSeq()
        if (input("Would you like to save the rectangles from this map in a text file? ").find("es")>-1):
            path= input("Input file path: ")
            with open(path, "w+") as file:
                file.write(json.dumps(self.doc, indent=4))

    def create_env_seed(self, text_file: str):
        """Creates environment based on seed contained in text_file"""
        f = open(text_file, "r")
        seed = f.read()

        is_curr_obs = seed[0] == '1'
        seed = seed[1:].rstrip()
        curr_row_ind = 0
        curr_col_ind = 0

        for curr_char in seed:
            run = ord(curr_char)
            # print('CURRENT CHAR: ')
            # print(curr_char)
            # print('CURRENT run length: ')
            # print(ord(curr_char))
            for i in range(run):
                if curr_row_ind >= 200:
                    raise Exception("seed length too long!")
                if curr_col_ind >= 200:
                    raise Exception("seed length too long!")
                # print('Curr col ind: ')
                # print(curr_col_ind)
                # print('Curr row ind: ')
                # print(curr_row_ind)
                # set the indices
                self.grid[curr_row_ind][curr_col_ind].is_obstacle = is_curr_obs
                curr_col_ind += 1
                # print('WHERE ARE WE IN RUN??? ')
                # print(i)
                # print(run)
                if curr_col_ind == 200:
                    curr_col_ind = 0
                    curr_row_ind += 1
            is_curr_obs = not is_curr_obs

    def create_env_json(self, text_file):
        """creates an environment by processing the text_file as a json containing categorical and numerical
        variables and then creating environment by assigning tiles to obstacles"""
        string= ''
        with open(text_file, 'r') as file:
            # read .txt file as string in json format
            for i in file.readlines():
                string+= i.strip()

        # convert string to python object
        j= json.loads(string)

        # set tiles to obstacle based on file contents
        for i in j:
            if i['type'] == 'rectangle':
                for row in self.grid[i['y']:i['y'] + i['height']]:
                    for cell in row[i['x']:i['x'] + i['width']]:
                        cell.is_obstacle = True
            if i['type']=='circle':
                for row_v in range(i['x']-i['radius'], i['x']+i['radius']+1):
                    for col_v in range(i['y']-i['radius'], i['y']+i['radius']+1):
                        if (row_v-i['x'])**2 + (col_v-i['y'])**2 <=i['radius']**2:
                            self.grid[row_v][col_v].is_obstacle= True
            if i['type']=='ellipse':
                for row_v in range(i['x']-i['x_radius'], i['x']+i['x_radius']+1):
                    for col_v in range(i['y']-i['y_radius'], i['y']+i['y_radius']+1):
                        if (float(row_v-i['x'])/i['x_radius'])**2 + (float(col_v-i['y'])/i['y_radius'])**2 <=1:
                            self.grid[row_v][col_v].is_obstacle= True
            if i['type']=='other-dots':
                for pair in i['dots']:
                    self.grid[pair[0]][pair[1]].is_obstacle= True


    def create_rand_env(self, prob):
        """Fills in grid rorally randomly

        Arguments:
        prob {int} -- 1/prob = the probability any tile is an obstacle
        """
        for grid_row in self.grid:
            for tile in grid_row:
                randomNum = random.randint(1, prob)
                if (randomNum == 1):
                    tile.is_obstacle = True
