import json
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
    terabee_bot_ang: Dict[int, int] = {0: 67.5, 1: 90, 2: 112.5, 3: 135, 4: 157.5, 5: 180, 6: 202.5,
                                       7: 225} #not plugged in

    def __init__(self, client=True):
        #needs manual correction later
        #self.lidar_ignore = (30, 70) # inclusive range of lidar data to be ignored

        # initialize to max-size values for socket bytesize testing
        # lidar array is of size 360 minus range of the angles to be ignored
        self.lidar: List[tuple[int, int]] = []

        # self.terabee_bot, self.terabee_mid, and self.terabee_top are lists of distances
        self.terabee_bot: List[int] = []
        self.terabee_mid: List[int] = []
        self.terabee_top: List[int] = []
        self.imu_array = []
        self.imu_count = 0
        self.heading_arr = [0] * 3
        self.heading = 0
        self.init_imu = [0, 0, 0]
        if client:
            TEST_API.init_serial('/dev/ttyTHS1', 38400) # port name may be changed depending on the machine
            self.init_imu = self.get_init_imu()


    def package_data(self):
        return [self.terabee_bot, self.terabee_mid, self.terabee_top, self.lidar]

    def set_lidar(self, data):
        self.lidar= [None]*360
        for i, j in data:
            self.lidar[i] = j

    def get_lidar(self):
        lidar_start_time = time.time()
        vis_map = {} # a dictionary associating angles with object distance
        TEST_API.decode_arrays()
        list_tup = TEST_API.get_array('LDR')
        for ang, dist in list_tup:
            # ignores angle data within the range to be ignored
            vis_map[ang] = dist
        # self.lidar = list(vis_map.items())

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
        # tan_x = math.tan(math.radians(imu_reading[0]))**2
        # tan_y = math.tan(math.radians(imu_reading[1]))**2
        # tan_z = math.tan(math.radians(imu_reading[2]))**2
        # x = math.sqrt(1 / ((tan_z+tan_z*tan_x) + 1))
        # y = math.sqrt(1 / ((tan_x+tan_x*tan_y) + 1))
        # z = math.sqrt(1 / ((tan_y+tan_z*tan_y) + 1))
        # return [x, y, z]
        # tan_x = math.tan(math.radians(imu_reading[0]))
        #tan_y = math.tan(math.radians(imu_reading[1]))
        # tan_z = math.tan(math.radians(imu_reading[2]))
        # x = 1
        # y = tan_z
        # z = tan_x * tan_z

        angle_x = math.radians(imu_reading[0]);
        # print("x " + str(angle_x))
        angle_y = math.radians(imu_reading[1]);
        # print("y " + str(angle_y))
        angle_z = math.radians(imu_reading[2]);
        # print("z " + str(angle_z))
        # phi = math.acos(math.cos(angle_x) * math.cos(angle_y))
        # theta = angle_z
        # x = math.sin(phi)*math.cos(theta)
        # y = math.sin(phi) * math.sin(theta)
        # z = math.cos(phi)

        x = imu_reading[0]
        y = imu_reading[1]
        z = imu_reading[2]
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
        # mag_init = np.linalg.norm(self.init_imu)
        # mag_curr = np.linalg.norm(self.heading_arr)
        curr_heading = self.heading_arr[0] - self.init_imu[0]
        print("init_imu" + str(self.init_imu))
        print("heading_arr" + str(self.heading_arr))
        # curr_heading = np.arccos(np.dot(self.init_imu, self.heading_arr)/(mag_init * mag_curr))
        print("curr heading" + str(curr_heading))
        #curr_heading = self.heading_arr[2]-self.init_imu[2]
        return (curr_heading+360)%360

    def update_imu(self):
        TEST_API.decode_arrays()
        print("IMU arrays is: ", TEST_API.get_array("IMU"))
        self.heading_arr = self.xyz_calc(TEST_API.get_array("IMU"))
        self.heading = self.calc_curr_heading()

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


    """"
    Return a JSON-formatted string with all the attributes of this SensorState object
    """
    def to_json(self):
        ans = {}
        ans['lidar'] = self.lidar
        ans['terabee_top'] = self.terabee_top
        ans['terabee_mid'] = self.terabee_mid
        ans['terabee_bot'] = self.terabee_bot
        ans['imu_array'] = self.imu_array
        ans['heading_arr'] = self.heading_arr
        ans['imu_count'] = self.imu_count
        ans['heading'] = self.heading
        ans['init_imu'] = self.init_imu
        return json.dumps(ans)

    """
    Populate this SensorState object with the values in input_json
    """
    def from_json(self, input_json):
        self.lidar = input_json['lidar']
        self.terabee_top = input_json['terabee_top']
        self.terabee_mid = input_json['terabee_mid']
        self.terabee_bot = input_json['terabee_bot']
        self.imu_array = input_json['imu_array']
        self.heading_arr = input_json['heading_arr']
        self.imu_count = input_json['imu_count']
        self.heading = input_json['heading']
        self.init_imu = input_json['init_imu']

    """
    Simulates a line of multiple objects spawning directly in front of C1C0
    """
    def front_obstacles(self):
        fake_lidar = [(angle+180, int(750/math.cos(math.radians(angle)))) for angle in range(0, 80, 10)]
        fake_lidar += [(180-angle, int(750/math.cos(math.radians(angle)))) for angle in range(10, 80, 10)]
        # fake_lidar = [(180, 500), (270, 500), (89, 500), (90, 500), (91, 500), (210, 577)]
        self.lidar = fake_lidar

    """
    Simulates an obstacle in each of the 4 corners of C1C0's vision
    """
    def four_corners(self):
        fake_lidar = [(60, 800), (120, 800), (240, 800), (300, 800)]
        self.lidar = fake_lidar

    """
    Simulates C1C0 spawning inside of an obstacle and in between a line of obstacles
    """
    def spawn_inside_obstacle_line(self):
        fake_lidar = [(angle, dist) for dist in range(401, 801, 100) for angle in range(90, 271, 90)]
        self.lidar = fake_lidar

    """
    Simulates a diamond around C1C0
    """
    def diamond(self):
        fake_lidar = [(angle*90, 700) for angle in range(4)]
        self.lidar = fake_lidar

    """
    Simulates a circle around C1C0 with a gap of size (parameter) size
    """
    def circle_gap(self, size):
        fake_lidar = [(angle, 900) for angle in range(0, 360-size, 1)]
        self.lidar = fake_lidar
        
    def reset_data(self):
        self.lidar = []



if __name__ == "__main__":
    sensor_state = SensorState()
    list = sensor_state.get_lidar()
    print(list)


