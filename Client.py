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
    sendData.send_data([[1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 2, 3], [4, 5, 6]])
    sendData.send_data({'a': 2})
    megaTest = []
    for i in range(100):
        megaTest.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
    sendData.send_data(megaTest)
