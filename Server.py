import pickle
from Network import *


class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        print("Server Started")

    def receive_data(self):
        return pickle.loads(self.socket.recvfrom(4096)[0])


# TEST
if __name__ == "__main__":
    receiveData = Server()
    while True:
        print(receiveData.receive_data())

"""
code for working with unlimited send size!
buffer = []
while True:
    data, addr = self.socket.recvfrom(4096)
    # data equals None
    if not data:
        break
    # when a message has been received
    print("Message from: " + str(addr))
    buffer.append(data)
    if b"END" in data:
        break
 print(pickle.loads(b"".join(buffer)))
"""