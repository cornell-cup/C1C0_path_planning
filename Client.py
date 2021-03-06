import pickle
from Network import *
from SensorState import *

class Client(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), 4005))

    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """
        self.socket.sendto(pickle.dumps(data), self.server)


# TEST
if __name__ == "__main__":
    sendData = Client()

    data_packet= SensorState()
    sendData.send_data(data_packet)
