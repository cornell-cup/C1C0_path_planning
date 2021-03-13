import pickle
from Network import *


class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        self.socket.settimeout(2)  # interferes with stopping
        print("Server Started")
        self.client = ("", 0)

    def receive_data(self):
        try:
            x = self.socket.recvfrom(4096)
            self.client = x[1]
            return pickle.loads(x[0])
        except socket.timeout:
            return "no data within listening time"

    ##  precondition: must have called receive_data successfully
    def send_update(self, update):
        self.socket.sendto(pickle.dumps(update), self.client)


# TEST
if __name__ == "__main__":
    computer = Server()
    while True:
        x = computer.receive_data()
        if x != "no data within listening time":
            print(x)
            computer.send_update(123321)  # placeholder
            break
