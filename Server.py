import pickle
from Network import *


class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        self.socket.settimeout(2)  # interferes with stopping
        print("Server Started")
        self.client= ("", 0)

    def receive_data(self):
        try:
            x= self.socket.recvfrom(4096)
            print(x[1:])
            return pickle.loads(x[0])
        except socket.timeout:
            return "no data within listening time"

    ## precondition: must have called receive_data successfully
    def send_update(self, update):
        # TODO: implement
        self.socket.sendto(1, self.client)


# TEST
if __name__ == "__main__":
    receiveData = Server()
    while True:
        x= receiveData.receive_data()
        if x!= "no data within listening time":
            print(x)
            break

