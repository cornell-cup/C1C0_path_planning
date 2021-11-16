from typing import List, Dict
import SensorCode.LIDAR_API as LIDAR_API
import SensorCode.TEST_API as TEST_API
import time
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
    terabee_bot_ang: Dict[int, int] = {}
    terabee_mid_ang: Dict[int, int] = {}
    terabee_top_ang: Dict[int, int] = {}

    def __init__(self):
        # initialize to max-size values for socket bytesize testing
        self.lidar: List[tuple[int, int]] = [1000]*360
        # self.terabee_bot, self.terabee_mid, and self.terabee_top are lists of distances
        self.terabee_bot: List[int] = [1]*8
        self.terabee_mid: List[int] = [1]*8
        self.terabee_top: List[int] = [1]*8
        self.imu_gyro: List[int] = [1]*3
        self.imu_linear_acc: List[int] = [1]*3
        self.heading: int = 0
        TEST_API.init_serial('/dev/ttyTHS1', 115200) #port name may be changed depending on the machine

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
        bot_ter = [] # bottom terabee list of tuples
        mid_ter = [] # mid terabee list of tuples
        top_ter = [] # top terabe list of tuples


        for counter, distance in (range(len(self.terabee_bot_ang)), self.terabee_bot_ang):
            bot_ter.append((counter, distance))

        for counter, distance in (range(len(self.terabee_mid_ang)), self.terabee_mid_ang):
            mid_ter.append((counter, distance))

        for counter, distance in (range(len(self.terabee_top_ang)), self.terabee_top_ang):
            top_ter.append((counter, distance))


        return bot_ter, mid_ter, top_ter


    def update_terabee(self):
        # set instance attributes terabee_bot, terabee_mid, and terabee_top to data returned by TERABEE sensor API
        # self.terabee_bot, self.terabee_mid, self.terabee_top = TERABEE_API.get_terabee_array()
        self.terabee_bot = TEST_API.get_array("TB1")
        self.terabee_mid = TEST_API.get_array("TB2")
        self.terabee_top = TEST_API.get_array("TB3")

    def get_imu(self):
        #set instance attributes imu_gyro and imu_linear_acc to data returned by IMU sensor API
        self.imu_gyro = TEST_API.get_array("IMUG")
        self.imu_linear_acc = TEST_API.get_array("IMUA")

    # def __str__(self):
    #     return "lidar: "+str(self.lidar) + "t_b: "+str(self.terabee_bot)

    def update(self) -> None:
        """
        Update function to read the serial lines and update the sensor state
        """
        self.update_terabee()
        self.lidar = self.get_lidar()
        self.get_imu()


if __name__ == "__main__":
    sensor_state = SensorState()


