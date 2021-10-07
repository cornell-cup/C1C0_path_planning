import pickle
from Networks.Network import *
from SensorCode.SensorState import *
import sys
import json
import time

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

class Client(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), 4005))
        #self.socket.settimeout(4)  # interferes with stopping
        self.receive_ID = 0

    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """
        x= pickle.dumps({'id': self.receive_ID, 'data': data})
        print("size: ", sys.getsizeof(x))
        print(data)
        self.socket.sendto(x, self.server)

    def listen(self):
        x = ["", ("0.0.0.0", 9999)]

        # according to pickle docs you shouldn't unpickle from unknown sources, so we have some validation here
        while x[1] != self.server:
            x = self.socket.recvfrom(4096)
        y = pickle.loads(x[0])

        self.receive_ID = y['id']
        return y['content']

# test to make sure that SensorState object is <= 4096 bytes
def connection_test():
    robot = Client()
    data_packet = SensorState()
    robot.send_data(data_packet)
    print(robot.listen())

def load_test():
    robot = Client()
    t = time.time()
    total_count = 0
    while time.time() - t < 1.0:
        data_packet = "hello world"
        robot.send_data(data_packet)
        total_count = robot.listen()
        time.sleep(0.1)
    robot.send_data("test over")
    print()
    print(total_count)

if __name__ == "__main__":
    load_test()
