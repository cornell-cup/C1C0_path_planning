import pickle
from Network import *


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
    lidarData = [(10, 10) for i in range(360)]
    terabee1 = [1 for i in range(20)]
    terabee2 = [1 for i in range(20)]
    terabee3 = [1 for i in range(20)]
    heading = 0

    data_packet = {'userinput':'', 'lidardata': lidarData, 'tarbee1': terabee1, 'tarabee2': terabee2, 'tarabee2': terabee3, 'heading': heading}
    while True:
        user_input = input()
        data_packet['userinput'] = user_input
        sendData.send_data(data_packet)
