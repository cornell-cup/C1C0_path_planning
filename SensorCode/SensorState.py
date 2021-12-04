from typing import List, Dict
import SensorCode.TEST_API as TEST_API
#import sys
#sys.path.append('/home/ccrt/c1c0-ece') #Might need to be resolved
#import TEST_API
import time
import math
import numpy as np

class SensorState:
    """
    Class to keep track of the state of the sensor inputs for C1C0, to be stored on Jetson
        Instance Attributes:
            lidar (List[tuple[int, int]]): List of lidar values, each element is an (ang,dist) tuple
            terabee_bot (List[int]): List of bottom terabee distances, each element is distance
            teerabee_mid (List[int]): List of mid terabee distances, each element is distance
            terabee_top (List[int]): List of top terabee distances, each element is distance
        Class Attributes:
            terabee_bot_ang (Dict[int, int]): mapping from indices in terabee array's to angle of reading
            terabee_mid_ang (Dict[int, int]): mapping from indices in terabee array's to angle of reading
            terabee_top_ang (Dict[int, int]): mapping from indices in terabee array's to angle of reading
    """
    terabee_top_ang: Dict[int, int] = {0: 0, 1: 22.5, 2: 45, 3: 67.5, 4: 90, 5: 112.5, 6: 135, 7: 157.5}
    terabee_mid_ang: Dict[int, int] = {0: 180, 1: 202.5, 2: 225, 3: 247.5, 4: 270, 5: 292.5, 6: 315, 7: 337.5}
    terabee_bot_ang: Dict[int, int] = {0: 0, 1: 45, 2: 90, 3: 135, 4: 180, 5: 225, 6: 270, 7: 315} #not plugged in

    def __init__(self):
        # initialize to max-size values for socket bytesize testing
        self.lidar: List[tuple[int, int]] = [1000]*360
        # self.terabee_bot, self.terabee_mid, and self.terabee_top are lists of distances
        self.terabee_bot: List[int] = [1]*8
        self.terabee_mid: List[int] = [1]*8
        self.terabee_top: List[int] = [1]*8
        self.imu_array = []
        self.imu_count = 0
        self.heading_arr = [0] * 3
        self.heading = 0
        TEST_API.init_serial('/dev/ttyTHS1', 115200) # port name may be changed depending on the machine
        # self.init_imu = self.get_init_imu()

    def package_data(self):
        return [self.terabee_bot, self.terabee_mid, self.terabee_top, self.lidar]

    def set_lidar(self, data):
        self.lidar= [None]*360
        for i, j in data:
            self.lidar[i] = j

    def get_lidar(self):
        lidar_start_time = time.time()
        vis_map = {} #a dictionary associating angles with object distance
        TEST_API.decode_arrays()
        list_tup = TEST_API.get_array('LDR')

        for ang, dist in list_tup:
            vis_map[ang] = dist
        print(f"One lidar poll takes {time.time() - lidar_start_time} seconds")
        return list(vis_map.items())


    def get_terabee(self):
        """

        :return: 3 lists of tuples representing (angle, distance) for bottom, mid, top terabee sensors respectively
        """

        bot_ter = []  # bottom terabee list of tuples
        mid_ter = []  # mid terabee list of tuples
        top_ter = []  # top terabee list of tuples

        counter = 0
        for distance in self.terabee_bot:
            bot_ter.append((self.terabee_bot_ang[counter],distance))
            counter += 1
        
        counter = 0
        for distance in self.terabee_mid:
            mid_ter.append((self.terabee_mid_ang[counter],distance))
            counter += 1
        
        counter = 0
        for distance in self.terabee_top:
            top_ter.append((self.terabee_top_ang[counter],distance))
            counter += 1

        # ~ for counter, distance in (range(len(self.terabee_bot_ang)), self.terabee_bot_ang):
            # ~ bot_ter.append((counter, distance))

        # ~ for counter, distance in (range(len(self.terabee_mid_ang)), self.terabee_mid_ang):
            # ~ mid_ter.append((counter, distance))

        # ~ for counter, distance in (range(len(self.terabee_top_ang)), self.terabee_top_ang):
            # ~ top_ter.append((counter, distance))


        return bot_ter, mid_ter, top_ter

    def update_terabee(self):
        # set instance attributes terabee_bot, terabee_mid, and terabee_top to data returned by TERABEE sensor API
        TEST_API.decode_arrays()
        self.terabee_top = TEST_API.get_array("TB1")
        self.terabee_mid = TEST_API.get_array("TB2")
        self.terabee_bot = TEST_API.get_array("TB3")

    def imu_average(self):
        x = 0
        y = 0
        z = 0
        for vector in self.imu_array:
            x += vector[0]
            y += vector[1]
            z += vector[2]
        return [x/10, y/10, z/10]

    def xyz_calc(self, imu_reading):
        """
        Takes in raw imu api data and converts into heading vector
        """
        tan_x = math.tan(math.radians(imu_reading[0]))**2
        tan_y = math.tan(math.radians(imu_reading[1]))**2
        tan_z = math.tan(math.radians(imu_reading[2]))**2
        x = math.sqrt(1 / ((tan_z+tan_z*tan_x) + 1))
        y = math.sqrt(1 / ((tan_x+tan_x*tan_y) + 1))
        z = math.sqrt(1 / ((tan_y+tan_z*tan_y) + 1))
        return [x, y, z]

    def get_init_imu(self):
        """
        calculates and updates initial imu
        """
        while self.imu_count < 10:
            TEST_API.decode_arrays()
            self.imu_array.append(self.xyz_calc(TEST_API.get_array("IMU")))
            self.imu_count += 1
        return self.imu_average()

    def calc_curr_heading(self):
        """
        Uses current heading_arr to calculate heading angle (angle between inital
        heading array and current heading array)
        """
        mag_init = np.linalg.norm(self.init_imu)
        mag_curr = np.linalg.norm(self.heading_arr)
        print("init_imu" + str(self.init_imu))
        print("heading_arr" + str(self.heading_arr))
        curr_heading = np.arccos(np.dot(self.init_imu, self.heading_arr)/(mag_init * mag_curr))
        print("curr heading" + str(curr_heading))
        return curr_heading

    def update_imu(self):
        TEST_API.decode_arrays()
        print("IMU arrays is: ", TEST_API.get_array("IMU"))
        # self.heading_arr = self.xyz_calc(TEST_API.get_array("IMU"))
        # self.heading = self.calc_curr_heading()

    def get_heading(self):
        return self.heading

        #set instance attributes imu_gyro and imu_linear_acc to data returned by IMU sensor API
        # self.imu_gyro = TEST_API.get_array("IMUG")
        # self.imu_linear_acc = TEST_API.get_array("IMUA")

    # def __str__(self):
    #     return "lidar: "+str(self.lidar) + "t_b: "+str(self.terabee_bot)

    def update(self) -> None:
        """
        Update function to read the serial lines and update the sensor state
        """
        self.update_terabee()
        self.lidar = self.get_lidar()
        self.update_imu()


if __name__ == "__main__":
    sensor_state = SensorState()


