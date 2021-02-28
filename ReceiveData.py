import socket
import pickle
from Tile import *


# server file,
class ReceiveData:
    def __init__(self):
        port = 4000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.get_ip(), port))
        print("Server Started")

    def receive_data(self):
        buffer = []
        while True:
            data, addr = self.s.recvfrom(1024)
            # data equals None
            if not data:
                break

            # when a message has been received
            print("Message from: " + str(addr))
            buffer.append(data)
            if b"qqqqq" in data:
                break
        print(pickle.loads(b"".join(buffer)))
        return pickle.loads(b"".join(buffer))

    def get_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP


# TEST
if __name__ == "__main__":
    receiveData = ReceiveData()
    while True:
        receiveData.receive_data()
