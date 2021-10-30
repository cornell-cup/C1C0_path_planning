from typing import List, Dict
import LIDAR_API
import TERABEE_API
import IMU_API
import TEST_API

class SensorState:
    """
    Class to keep track of the state of the sensor inputs for C1C0, to be stored on Jetson
        Instance Attributes:
            lidar (List[tuple[int, int]]): List of lidar values, each element is an (ang,dist) tuple
            terabee_bot (List[int]): List of bottom terabee distances, each element is distance
            teerabee_mid (List[int]): List of mid terabee distances, each element is distance
            terabee_top (List[int]): List of top terabee distances, each element is distance
            pos_x (int): X position of hedgehog in GPS sub-map
            pos_y (int): Y position of hedgehog in GPS sub-map
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
        self.terabee_bot: List[int] = [1]*8
        self.terabee_mid: List[int] = [1]*8
        self.terabee_top: List[int] = [1]*8
        self.imu_gyro: List[int] = [1]*3
        self.imu_linear_acc: List[int] = [1]*3
        self.heading: int = 0
        LIDAR_API.init_serial('/dev/ttyTHS1', 38400)

    def package_data(self):
        return [self.terabee_bot, self.terabee_mid, self.terabee_top, self.lidar]

    def set_lidar(self, data):
        self.lidar= [None]*360
        for i, j in data:
            self.lidar[i] = j

    def get_lidar(self):
        vis_map = {} #a dictionary associating angles with object distance
        vis_angles = [False] * 360 #List of visited angles with a margin of +-2
        count = 0
        while count < 360:
            # list_tup = LIDAR_API.get_LIDAR_tuples()
            list_tup = TEST_API.get_array("LDR")
            print(list_tup)
            for ang, dist in list_tup:
                print(ang)
                if ang not in vis_map:
                    for index_offset in [-2, -1, 0, 1, 2]:
                        #angles with +-2 of read-in angle are also treated as visited
                        print("test: " + str(ang-index_offset) + " ")
                        if ang-index_offset >= 0 and ang-index_offset < 360 and not vis_angles[ang-index_offset]:
                            vis_angles[ang-index_offset] = True
                            count += 1
                vis_map[ang] = dist
        # self.lidar = list(vis_map.items())
        return list(vis_map.items()) #or just do line above and refactor servergui?

        # ans= []
        # for i, j in enumerate(self.lidar):
        #     if j==None:
        #         continue
        #     ans.append((i,j))
        # return ans

    def get_terabee(self):
        # set instance attributes terabee_bot, terabee_mid, and terabee_top to data returned by TERABEE sensor API
        # self.terabee_bot, self.terabee_mid, self.terabee_top = TERABEE_API.get_terabee_array()
        self.terabee_bot = TEST_API.get_array("TB1")
        self.terabee_mid = TEST_API.get_array("TB2")
        self.terabee_top = TEST_API.get_array("TB3")

    def get_imu(self):
        #set instance attributes imu_gyro and imu_linear_acc to data returned by IMU sensor API
        self.imu_gyro = TEST_API.get_array("IMUG")
        self.imu_linear_acc = TEST_API.get_array("IMUA")

    def __str__(self):
        return "lidar: "+str(self.lidar) + "t_b: "+str(self.terabee_bot)

    def update(self) -> None:
        """
        Update function to read the serial lines and update the sensor state
        """
        self.get_terabee()
        self.lidar = self.get_lidar()
        self.get_imu()


if __name__ == "__main__":
    sensor_state = SensorState()
    try:
        # ~ print(LIDAR_API.get_LIDAR_tuples())
        print(sensor_state.get_lidar())
    except KeyboardInterrupt:
        LIDAR_API.ser.close()

