import pickle
from Network import *
from SensorState import *
import time

class Client(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), 4005))
        #self.socket.settimeout(4)  # interferes with stopping

    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """
        self.socket.sendto(pickle.dumps(data), self.server)

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
