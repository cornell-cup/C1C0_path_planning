import pickle
from Network import *


class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        print("Server Started")
        self.client = ("", 0)

    def receive_data(self):
        try:
            x = self.socket.recvfrom(4096)
            self.client = x[1]
            self.socket.settimeout(2)  # interferes with stopping on further calls
            return pickle.loads(x[0])
        except socket.timeout:
            self.socket.settimeout(2)  # interferes with stopping on further calls
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
