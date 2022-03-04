import pickle
from Networks import *
import sys
import json
import time
from SensorCode import SensorState
from matplotlib import pyplot as plt
import csv

sys.setrecursionlimit(10000)

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


class Client(Network):
    def __init__(self):
        super().__init__()
        # this used to be 4005, make sure to check this
        self.socket.bind((self.get_ip(), 4004))
        # self.socket.settimeout(4)  # interferes with stopping
        self.receive_ID = 0

    def init_send_data(self, data):
        """
        initial send that requires a confirmation to move on
        """
        x = json.dumps({'id': self.receive_ID, 'data': data}).encode('utf-8')
        self.socket.settimeout(1)
        self.socket.sendto(x, self.server)
        try:
            x = self.socket.recvfrom(4096)
            received = json.loads(x[0].decode('utf-8'))
            print(f"initial data received: {received}")
            self.socket.settimeout(None)
        except:
            print("CLIENT SEND FAILED")
            self.init_send_data(data)

    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """
        try:
            x = json.dumps({'id': self.receive_ID, 'data': data}).encode('utf-8')
        except RecursionError:
            print("failed on ", data, "hello")
            raise RecursionError
        # print("size: ", sys.getsizeof(x))
        # print(data)
        self.socket.sendto(x, self.server)

    def listen(self):
        x = ["", ("0.0.0.0", 9999)]
        
        # according to pickle docs you shouldn't unpickle from unknown sources, so we have some validation here
        while x[1] != self.server:
            try:
                x = self.socket.recvfrom(4096)
            except socket.timeout:
                pass
        y = json.loads(x[0].decode('utf-8'))

        self.receive_ID = y['id']
        return y['content']


def load_test():
    size = 360
    robot = Client()
    t = time.time()
    num_success = 0
    sensor_state = {
        "lidar": [(i, 0) for i in range(size)],
        "terabee_top": [i for i in range(size)],
        "terabee_mid": [i for i in range(size)],
        "terabee_bot": [i for i in range(size)],
        "imu_array": [i for i in range(size)],
        "heading_arr": [0, 0, 0],
        "imu_count": 360,
        "heading": 0
    }
    arr = [0]
    t_last = time.time()
    PACKETS = 10
    too_long = 0
    rows = []
    x = int(previousIndex()) + 1
    for i in range(PACKETS):
        robot.send_data(sensor_state)
        robot.listen()
        num_success += 1
        t = time.time()
        arr.append(t - t_last)
        t_last = t
        if arr[-1] > 0.5:
            too_long += 1
        rows.append(str(x) + ',' + str(arr[-1]) + '\n')
        x += 1
    robot.send_data("done-over")
    print(arr)
    print(too_long)
    plt.scatter(range(PACKETS), arr[1:])
    plt.show()
    with open("json_timing.csv", 'a') as file:
        file.writelines(ls)
        file.close()

# test to make sure that SensorState object is <= 4096 bytes
if __name__ == "__main__":
    load_test()
