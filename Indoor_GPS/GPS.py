from Indoor_GPS.marvelmind import MarvelmindHedge
from Constants.Consts import *
import time

class GPS():

    def __init__(self, grid, pid):
        # create Marvel Mind Hedge thread
        # get USB port with ls /dev/tty.usb*
        # adr is the address of the hedgehog beacon!
        self.hedge = MarvelmindHedge(tty=tty, adr=hedge_addr, debug=False)
        # start thread
        self.hedge.start()
        # REQUIRED SLEEP TIME in order for thread to start and init_pos to be correct
        time.sleep(1)
        # data in array's [usnadr, x, y, z, timestamp]
        self.init_pos = self.hedge.position()
        self.init_pos = [self.init_pos[0], self.init_pos[2], self.init_pos[1]*-1, self.init_pos[3], self.init_pos[4]]
        self.location_buffer = []
        self.grid = grid
        self.pid = pid

    def update_loc(self, curr_tile):
        """
        updates the current tile based on the GPS input
        """
        # call indoor gps get location function
        # avgPosition = [0, 0]
        # for prev_pos in self.location_buffer:
        #     if prev_pos is not None:
        #         avgPosition[0] += prev_pos[0]
        #         avgPosition[1] += prev_pos[1]

        # if len(self.location_buffer) >= 5:
        #     try:
        #         avgPosition[0] /= len(self.location_buffer)
        #         avgPosition[1] /= len(self.location_buffer)
        [_, y, x, z, ang, time] = self.hedge.position()
        x = -x
        x1 = x
        y1 = y

        self.location_buffer.pop(0)
        self.location_buffer.append((x1, y1))
        # map the position to the correct frame of reference
        x = (x - self.init_pos[1]) * 10
        y = (y - self.init_pos[2]) * 10
        x = int(tile_num_width/2) + int(x * 100 / tile_size)
        y = int(tile_num_height/2) + int(y * 100 / tile_size)
        prev_tile = curr_tile
        curr_tile = self.grid.grid[x][y]
        self.pid.update_PID(curr_tile.x, curr_tile.y)

        return prev_tile, curr_tile
        #     except:
        #         print("GPS Reads robot position is off the screen!")
        #         self.update_loc(curr_tile)
        # else:
        #     print("IN GPS ELSE ")
        #     [_, y, x, z, ang, time] = self.hedge.position()
        #     x = -x
        #     x1 = x
        #     y1 = y
        #     self.location_buffer.append((x1, y1))
        #
        #     return self.update_loc(curr_tile)
