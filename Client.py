import pickle
from Network import *
from SensorState import *
import time
import sys
import json

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

class Client(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), 4005))
        #self.socket.settimeout(4)  # interferes with stopping
        self.i= 1
    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """

        print("send number: ", self.i)
        self.i+= 1
        x= pickle.dumps(data)
        print("size: ", sys.getsizeof(x))
        print(data)
        self.socket.sendto(x, self.server)

    def listen(self):
        x = ["", ("0.0.0.0", 9999)]

        # according to pickle docs you shouldn't unpickle from unknown sources, so we have some validation here
        while x[1] != self.server:
            x = self.socket.recvfrom(4096)
        return pickle.loads(x[0])


# test to make sure that SensorState object is <= 4096 bytes
if __name__ == "__main__":
    robot = Client()
    data_packet= SensorState()
    robot.send_data(data_packet)
