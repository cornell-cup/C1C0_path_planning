import socket, pickle
import time
class SendData:
    def __init__(self):
        host= '192.168.86.79'
        self.server = ('192.168.86.83', 4000)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, 4005))

    def send_data(self, data):
        """sends json-like nested data containing sensor, accelerometer, etc.
        """
        self.socket.sendto(pickle.dumps(data) + b"qqqqq", self.server)

### TEST
if __name__ == "__main__":
    sendData = SendData()
    sendData.send_data([[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9]])
    sendData.send_data([[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9]])
    sendData.send_data({'a': 2})
    sendData.send_data([[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9]])
    sendData.send_data([[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9]])