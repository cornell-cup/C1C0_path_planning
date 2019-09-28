def setup():
    size(2000, 1500)
    stroke(255)
    background(192, 64, 0)
    # frameRate(5)
    

counter = 0
alreadyClicked = False
    


def mouseIsClicked():
    return mousePressed and counter == 1

tileSize = 50

class Tile:
    x = 0
    y = 0
    def __init__(self, x, y, indexX, indexY):
        # self.size = tiles_size
        self.x = indexX
        self.y = indexY
        # free, wall, start, target
        self.type = "free"
        self.neighbors = []
        
    def setNeighbors(self, neighbors):
        self.neighbors = neighbors

    def addNeighbors(self, neighbor):
        self.neighbors.push(neighbors)
        
    def getNeighbors(self):
        return self.neighbors
    
    def getHashCode(self):
        return str(self.x) + "," + str(self.y)

class Grid:
    tiles = []
    def __init__(self, tileLength, tilesX, tilesY):
        self.tileSize = tileLength
        self.tiles = self.createGrid(tilesX, tilesY) #2d list of tiles
        self.tilesX = tilesX
        self.tilesY = tilesY
        
        self.selected = False
        self.selectedNeighbor = False
        
        self.numObstacles = 80

    def createGrid(self, tilesX, tilesY):
        newTiles = []
        for x in range(tilesX):
            inner = []
            for y in range(tilesY):
                inner.append(Tile(tileSize * x, tileSize * y, x, y))
            newTiles.append(inner)
        return newTiles

    def getTile(self, x, y):
        if self.isValidTile(x, y):
            return self.tiles[x][y]
        else:
            return None
        
    def getTileFromCoords(self, x, y):
        return self.getTile(x/self.tileSize, y/self.tileSize)
        
        
    def addObstacles(self):
        for i in range(self.numObstacles):
            x = floor(random(0, len(self.tiles)))
            y = floor(random(0, len(self.tiles[0])))
            
            # if (x == self.startTile.x and y == self.startTile.y) or (x == self.targetTile.x and y == self.targetTile.y):
            #     self.tiles[x][y].type = self.tiles[x][y].type
            # else:
            self.tiles[x][y].type = "wall"
    
    # adds a reference to valid+free tile to each tile
    def loadNeighbors(self):
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[0])):
                self.tiles[x][y].setNeighbors(self.getNeighborsOf(x, y, False))
                
    # checks if the tile is within the bounds
    def isValidTile(self, tileX, tileY):
        return (tileX >= 0 and tileY >= 0 and
        tileX < len(self.tiles) and tileY < len(self.tiles[0]))
    
    # checks if tile is not marked as a wall
    def isFreeTile(self, tileX, tileY):
        return (self.tiles[tileX][tileY].type != "wall")
    
    def isFree(self, tile):
        return tile.type != "wall"
            
    # returns list of neighbors that are not obstructed
    def getNeighborsOf(self, tileX, tileY, allowDiagClipping = False):
        neighbors = []
        # walls can't have neighbors
        if (self.isFreeTile(tileX, tileY)):
            if (self.isValidTile(tileX - 1, tileY - 1) and self.isFreeTile(tileX - 1, tileY - 1)):
                # both top and left need to be valid
                if (self.isFreeTile(tileX, tileY - 1) and self.isFreeTile(tileX - 1, tileY)) or allowDiagClipping:
                    neighbors.append(self.tiles[tileX - 1][tileY - 1])
            
            if (self.isValidTile(tileX - 1, tileY) and self.isFreeTile(tileX - 1, tileY)):
                neighbors.append(self.tiles[tileX - 1][tileY])
            
            if (self.isValidTile(tileX - 1, tileY + 1) and self.isFreeTile(tileX - 1, tileY + 1)):
                # both bottom and left need to be valid
                if (self.isFreeTile(tileX, tileY + 1) and self.isFreeTile(tileX - 1, tileY)) or allowDiagClipping:
                    neighbors.append(self.tiles[tileX - 1][tileY + 1])
            
            if (self.isValidTile(tileX, tileY - 1) and self.isFreeTile(tileX, tileY - 1)):
                neighbors.append(self.tiles[tileX][tileY - 1])
            
            if (self.isValidTile(tileX, tileY + 1) and self.isFreeTile(tileX, tileY + 1)):
                neighbors.append(self.tiles[tileX][tileY + 1])
                
            if (self.isValidTile(tileX + 1, tileY - 1) and self.isFreeTile(tileX + 1, tileY - 1)):
                # both top and right need to be valid
                if (self.isFreeTile(tileX, tileY - 1) and self.isFreeTile(tileX + 1, tileY)) or allowDiagClipping:
                    neighbors.append(self.tiles[tileX + 1][tileY - 1])
            
            if (self.isValidTile(tileX + 1, tileY) and self.isFreeTile(tileX + 1, tileY)):
                neighbors.append(self.tiles[tileX + 1][tileY])
            
            if (self.isValidTile(tileX + 1, tileY + 1) and self.isFreeTile(tileX + 1, tileY + 1)):
                # both bottom and right need to be valid
                if (self.isFreeTile(tileX, tileY + 1) and self.isFreeTile(tileX + 1, tileY)) or allowDiagClipping:
                    neighbors.append(self.tiles[tileX + 1][tileY + 1])
        return neighbors
    
    def getNeighborsOfTile(self, tile, allowDiagClipping = False):
        return getNeighborsOf(tile.x, tile.y, allowDiagClipping)
    
    def getNighborsFromHashCode(self, hashcode, allowDiagClipping = False):
        strings = hashcode.split(",")
        ints = [int(strings[0]), int(strings[1])]
        return getNeighborsOf(ints[0], ints[1], allowDiagClipping)
                
    # gets tile index from pixel coordinates
    def getTileFrontCoords(self, x, y):
        tileX = x/self.tileSize
        tileY = y/self.tileSize
        
        tile = None
        if self.isValidTile(x, y):
            tile = self.tiles[x][y]
        return tile

# wraps a Tile so that we can do extra work with Tiles
class TileWrapper:
    def __init__(self, tile, parent = None, futureCost = 0, accCost = 0):
        self.tile = tile
        self.parent = parent
        self.futureCost = futureCost
        self.accCost = accCost
        
    # can set parent in future
    def setParent(self, parent):
        self.parent = parent
        
    def reset(self):
        self.parent = 0
        #self.futureCost = 0
        #slef.accCost = 0
        
    def cost(self):
        return self.futureCost + self.accCost
    
    def getTile(self):
        return self.tile
    
    def hash(self):
        return self.tile.getHashCode()
    
    def hasSameTile(self, tw):
        return tw.getTile().x == self.getTile().x and tw.getTile().y == self.getTile().y



# wrapper class for dictionaries enforcing type
class TileDict:
    def __init__(self, drawObj):
        self.dict = {}
        self.drawObj = drawObj
    
    def insert(self, hash, tileWrapper):
        self.dict[hash] = tileWrapper
        print("    inserted " + hash + "\t\tsize: " + str(len(list(self.dict.keys()))))
        pushMatrix()
        translate(tileWrapper.getTile().x * 50, tileWrapper.getTile().y * 50)
        self.drawObj["draw"]()
        popMatrix()
    
    def get(self, hash):
        return self.dict.get(hash)
    
    def mem(self, hash):
        exists = self.get(hash) != None
        
        return exists
    
    def pop(self, hash):
        if self.mem(hash):
            print("    popped " + hash)
            self.dict.pop(hash)
            
    def values(self):
        return self.dict.values()
    
    def clear(self):
        self.dict.clear()
        
    def toStr(self):
        return '([%s])' % ', '.join(map(str, list(self.dict.keys())))
    
def drawWhite():
    fill(255, 255, 255, 100)
    rect(0, 0, 50, 50)
def drawCross():
    stroke(0)
    line(0, 0, 50, 50)
    line(50, 0, 0, 50)

class Search:
    def __init__(self, grid):
        
        self.grid = grid
        
        self.targetTile = None
        self.startTile = None
        self.targetTileWrapper = None
        self.startTileWrapper = None
        self.finalTileWrapper = None
        
        self.ready = False
        
        # parallel lists of TileWrappers
        self.openListWrapper = TileDict({"draw": drawWhite})
        self.visitedListWrapper = TileDict({"draw": drawCross})
        
        self.maxIterations = 200
    
    def reset(self):
        self.openListWrapper.clear()
        self.visitedListWrapper.clear()
        self.finalTileWrapper = None
        
        self.ready = True
        
        self.startTile = self.grid.getTileFromCoords(max(min(mouseX, self.grid.tileSize * self.grid.tilesX - 10), 1),
                                                     max(min(mouseY, self.grid.tileSize * self.grid.tilesY - 10), 1))
        
        while (self.targetTile == None or self.targetTile.type == "wall"):
            self.targetTile = self.grid.getTile(floor(random(0, 5)), floor(random(len(self.grid.tiles[0]) - 5, len(self.grid.tiles[0]))))
        
        self.startTileWrapper = TileWrapper(self.startTile, None, 0, 0)
        self.targetTileWrapper = TileWrapper(self.targetTile, None, 0, 0)


    # returns a TileWrapper representing the final tile, or None
    def search(self):
        if self.startTile != None and self.grid.isFree(self.startTile) and self.startTileWrapper != None:
            iter = 0
            
            # populate visited lists
            # self.visitedListWrapper[self.startTileWrapper.getTile]
            
            
            # populate openlists - do you REALLY need a tile list copy of Wrapper list?
            firstOpenList = self.startTileWrapper.tile.getNeighbors()
            if (len(firstOpenList) <= 0):
                self.finalTileWrapper = None
                return
            
        
            # box each into TileWrapperss
            for tile in firstOpenList:
                newTileWrapper = TileWrapper(tile, self.startTileWrapper,
                            self.hybridDist(tile, self.targetTile),
                            self.hybridDist(self.startTile, tile))
                self.openListWrapper.insert(newTileWrapper.hash(), newTileWrapper)
            
            currentLeast = self.getLeastCostTileWrapper()
            

            # begin the real search algorithm
            while iter < min(self.maxIterations, 500):
                
                
                # choose the open wrapper with the lowest cost
                # we already have the least cost wrapper
                
                # if it is None, then we have failure (when through all tilES, but did NOT find target)
                if currentLeast == None:
                    # self.finalTileWrapper = None
                    print("CRITICAL FAILURE: went through all tiles, but did not find target")
                    return
                
                
                # add this wrapper to the visited, since we chose it
                self.visitedListWrapper.insert(currentLeast.hash(), currentLeast)
                # remove from openList
                
                self.openListWrapper.pop(currentLeast.hash())
                
                # check if this visited tile has the same tile, since if it is, it must
                # inductively be the last of the "best" path to the end
                if currentLeast.hasSameTile(self.targetTileWrapper):
                    self.finalTileWrapper = currentLeast
                    print("TARGET TILE FOUND")
                    return
                
                # get its neighbors, add them if not already in open list
                newOpenListTiles = currentLeast.getTile().getNeighbors()
                
                
                for tile in newOpenListTiles:
                    # only add if not in openlistwrapper and not in visitedlistwrapper
                    newTileWrapper = TileWrapper(tile, currentLeast,
                            self.hybridDist(tile, self.targetTile),
                            self.hybridDist(self.startTile, tile))
                    
                    notInOpen = not self.openListWrapper.mem(newTileWrapper.hash())
                    notInVisited = not self.visitedListWrapper.mem(newTileWrapper.hash())
                    
                    print(notInOpen, notInVisited)
                    # if not already in open list and not in visited, add to pen list
                    if (notInOpen and notInVisited):
                        
                        self.openListWrapper.insert(newTileWrapper.hash(), newTileWrapper)
                        
                currentLeast = self.getLeastCostTileWrapper()
                
                print("chose open: " + currentLeast.hash())
                iter = iter + 1
            # algorithm failure; did not find the tile in few enough tries; break out of function
            print("CRITICAL FAILURE: went through max iterations, but did not find target")
            return
        
    def manhattanDist(self):
        return 0
    
    def getLeastCostTileWrapper(self):
        returnTileWrapper = None
        for tileWrapper in self.openListWrapper.values():
            if returnTileWrapper == None:
                returnTileWrapper = tileWrapper
            if returnTileWrapper.cost() >= tileWrapper.cost():
                returnTileWrapper = tileWrapper
        return returnTileWrapper
    
    # treats a distanec as a sum of a diagonol and a straight line
    # more "realistic" in the real world (if there are few obstacles)
    def hybridDist(self, tile1, tile2):
        minDifference = 0
        distance = 0
        
        # get the "smaller difference" so that we can calculate the diagonal distance cost
        minDifference = min(abs(tile1.x - tile2.x), abs(tile1.y - tile2.y))
        
        if abs(tile1.x - tile2.x) > abs(tile1.y - tile2.y):
            # minDifference = abs(startTile.y - targetTile.y)
            distance = 1.4 * minDifference + (abs(tile1.x - tile2.x) - minDifference)
        else:
            # minDifference = abs(startTile.x - targetTile.x)
            distance = 1.4 * minDifference + (abs(tile1.y - tile2.y) - minDifference)
        return distance
        
        
    def update(self):
        if mousePressed:
            self.reset()
            self.search()
            
    def draw(self):
        fill(255, 180, 100);
        stroke(255)
        strokeWeight(1)
        
        if (self.ready):
            fill(100, 255, 0)
            rect(self.startTile.x * self.grid.tileSize, self.startTile.y * self.grid.tileSize, self.grid.tileSize, self.grid.tileSize)
            
            fill(255, 100, 100)
            rect(self.targetTile.x * self.grid.tileSize, self.targetTile.y * self.grid.tileSize, self.grid.tileSize, self.grid.tileSize)

            # print("found path? " + str(self.finalTileWrapper != None))
            if self.finalTileWrapper != None:
                fill(0, 0, 0)
                
                traver = self.finalTileWrapper
                
                while (traver.parent != None):
                    noStroke()
                    ellipse((traver.getTile().x + 0.5) * self.grid.tileSize, (traver.getTile().y + 0.5) * self.grid.tileSize, 10, 10)
                    
                    traver = traver.parent
    

            
grid = Grid(50, 30, 20)
grid.addObstacles()
grid.loadNeighbors()

search = Search(grid)

mouseXPrev = 0
mouseYPrev = 0
mouseTileX = 0
mouseTileY = 0

mouseTileXPrev = 0
mouseTileYPrev = 0

def mouseChanged():
    return mouseXPrev != mouseX or mouesYPrev != mouseY

def mouseTileChanged():
    return mouseTileXPrev != mouseTileX or mouseTileYPrev != mouseTileY

def drawGrid():
    for x in range(len(grid.tiles)):
        for y in range(len(grid.tiles[x])):
            fill(255, 180, 100);
            stroke(255)
            strokeWeight(1)
            if (grid.tiles[x][y].type == "wall"):
                fill(255, 255, 255)
            if (grid.tiles[x][y].selected):
                fill(255, 80, 0)
                
            rect(grid.tiles[x][y].x * grid.tileSize, grid.tiles[x][y].y * grid.tileSize, grid.tileSize, grid.tileSize);
            
            if (grid.tiles[x][y].selectedNeighbor):
                fill(255, 255, 255, 100)
                rect(grid.tiles[x][y].x * grid.tileSize, grid.tiles[x][y].y * grid.tileSize, grid.tileSize, grid.tileSize);
            


def updateGrid():
    fill(0)
    for x in range(len(grid.tiles)):
        for y in range(len(grid.tiles[x])):
            grid.tiles[x][y].selected = False
            grid.tiles[x][y].selectedNeighbor = False
    if (grid.isValidTile(mouseX/grid.tileSize, mouseY/grid.tileSize)):
        selectedTile = grid.tiles[mouseX/grid.tileSize][mouseY/grid.tileSize]
        selectedTile.selected = True
        for i in range(len(grid.tiles[mouseX/grid.tileSize][mouseY/grid.tileSize].neighbors)):
            grid.tiles[mouseX/grid.tileSize][mouseY/grid.tileSize].neighbors[i].selectedNeighbor = True
            

    

def draw():
    background(0);
    fill(255, 200, 0);
    rect(mouseX, mouseY, 10, 10)
    
    global counter
    
    if mousePressed:
        counter = counter + 1
    else:
        counter = 0
    
    global mouseTileX
    global mouseTileY
    global mouseTileXPrev
    global mouseTileYPrev
    
    mouseTileX = mouseX/grid.tileSize
    mouseTileY = mouseY/grid.tileSize
    
    updateGrid()
    
    drawGrid()
    
    search.update()
    
    search.draw()
    
    # print(mouseTileX, mouseTileY, mouseTileXPrev, mouseTileYPrev)
    
    # if (mouseChanged() and grid.isValidTile(mouseX/grid.tileSize, mouseY/grid.tileSize)):
    #     print("tile at " + str(mouseX/grid.tileSize) + ", " + str(mouseY/grid.tileSize), "neighbors: " + str(len(grid.tiles[mouseX/grid.tileSize][mouseY/grid.tileSize].neighbors)),
    #           "free: " + str(grid.isFreeTile(mouseX/grid.tileSize, mouseY/grid.tileSize)))
        
    mouseXPrev = mouseX
    mouseYPrev = mouseY
    
    if mouseTileXPrev != mouseTileX:
        mouseTileXPrev = mouseTileX
        mouseTileYPrev = mouseTileY
    
