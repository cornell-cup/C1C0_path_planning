from Indoor_GPS.marvelmind import MarvelmindHedge
from Constants.Consts import *
import time

class GPS():

    def __init__(self, grid, pid):
        # create Marvel Mind Hedge thread
        # get USB port with ls /dev/tty.usb*
        # adr is the address of the hedgehog beacon!
        self.hedge = MarvelmindHedge(tty=tty, adr=adr, debug=False)
        # start thread
        self.hedge.start()
        # REQUIRED SLEEP TIME in order for thread to start and init_pos to be correct
        time.sleep(1)
        # data in array's [x, y, z, timestamp]
        self.init_pos = self.hedge.position()
        self.location_buffer = [None]*4
        self.grid = grid
        self.pid = pid

    def update_loc(self, curr_tile):
        """
        updates the current tile based on the GPS input
        """
        # call indoor gps get location function
        avgPosition = [0, 0]
        total = 0
        for i in self.location_buffer:
            if i == None:
                continue
            avgPosition[0] += i[0]
            avgPosition[1] += i[1]
            total += 1

        if total == 0:
            pass
        else:
            avgPosition[0] /= total
            avgPosition[1] /= total

        [_, y, x, z, ang, time] = self.hedge.position()
        x = -x
        x1 = x
        y1 = y

        self.location_buffer.pop(0)
        self.location_buffer.append([x1, y1])
        # map the position to the correct frame of reference
        x = (x - self.init_pos[1]) * 10
        y = (y - self.init_pos[2]) * 10
        x = int(tile_num_width/2) + int(x * 100 / tile_size)
        y = int(tile_num_height/2) + int(y * 100 / tile_size)
        prev_tile = curr_tile
        curr_tile = self.grid.grid[x][y]
        self.pid.update_PID(curr_tile.x, curr_tile.y)

        return prev_tile, curr_tile
