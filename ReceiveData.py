import socket
import pickle
from Tile import *
from tkinter import *

## server file, 
class ReceiveData:
    host = '0.0.0.0'
    def __init__(self, host):
        self.host = host  # Server ip
        port = 4000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((host, port))
        print("Server Started")

    
    def receive_data(self):
        buffer = []
        while True:
            data, addr = self.s.recvfrom(4096)
            # data equals None
            if not data:
                break

            # when a message has been received
            print("Message from: " + str(addr))
            buffer.append(data)
            
        return pickle.loads(b"".join(buffer))

### TEST
if __name__ == "__main__":
    receiveData = ReceiveData("192.168.86.79")
    print(receiveData.receive_data())
