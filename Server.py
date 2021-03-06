import pickle
from Network import *


class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        print("Server Started")
        self.client = ("", 0)
        self.last_sent= None

    def receive_data(self):
        try:
            x = self.socket.recvfrom(4096)
            self.client = x[1]
            self.socket.settimeout(1)  # interferes with stopping on further calls
            return pickle.loads(x[0])
        except socket.timeout:
            self.send_update(self.last_sent) # re-attempt last send operation
            self.socket.settimeout(1)  # interferes with stopping on further calls
            return self.receive_data()

    ##  precondition: must have called receive_data successfully
    def send_update(self, update):
        self.last_sent= update
        self.socket.sendto(pickle.dumps(update), self.client)


# test with Client.py main method
if __name__ == "__main__":
    computer = Server()
    while True:
        x = computer.receive_data()
        if x != "no data within listening time":
            print(x)
            computer.send_update(123321)  # placeholder
            break
