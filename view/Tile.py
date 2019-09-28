class Tile:

    def __init__(self, tile_size, occupied = False):
        self.size = tiles_size
        self.isOccupied = occupied

    """
    Changes the occupancy status of the tile
    Note: we are only working with static objects for now
    """
    def changeOccupancy(self):
        self.isOccupied = not (self.isOccupied)
