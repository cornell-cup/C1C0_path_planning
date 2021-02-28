import pickle
from Network import *


class Client(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), 4005))

    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """
        self.socket.sendto(pickle.dumps(data) + b"END", self.server)


# TEST
if __name__ == "__main__":
    sendData = Client()
    lidarData = [(10, 10) for i in range(360)]
    tarabee1 = [1 for i in range(20)]
    tarabee2 = [1 for i in range(20)]
    heading = 0

    data_packet = {'lidar': lidarData, 'tarbee1': tarabee1, 'tarabee2': tarabee2, 'heading': heading}

    sendData.send_data(data_packet)
