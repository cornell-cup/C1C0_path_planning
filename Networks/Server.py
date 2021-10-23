import pickle
from Networks.Network import *
import time

class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        print("Server Started")
        self.client = ("", 0)
        self.last_sent= None
        self.send_ID = 0
        self.start_time = time.time()
        self.num_latency_prints = 0

    def receive_data(self):
        try:
            x = self.socket.recvfrom(4096)
            self.client = x[1]
            self.socket.settimeout(1)  # interferes with stopping on further calls
            y = pickle.loads(x[0])
            if y['id'] != self.send_ID:
                self.send_update(self.last_sent)  # re-attempt last send operation
                self.socket.settimeout(1)  # interferes with stopping on further calls
                return self.receive_data()
            return y['data']
        except socket.timeout:
            self.send_update(self.last_sent) # re-attempt last send operation
            self.socket.settimeout(1)  # interferes with stopping on further calls
            return self.receive_data()

    #  precondition: must have called receive_data successfully
    def send_update(self, update):
        self.send_ID += 1
        self.last_sent = update
        if int(time.time() - self.start_time) >= self.num_latency_prints + 1:
            print(f"The packet frequency is {int(self.send_ID / int(time.time() - self.start_time))} updates per second")
            self.num_latency_prints += 1
        self.socket.sendto(pickle.dumps({'id': self.send_ID, 'content': update}), self.client)


# test with Client.py main method
def connection_test():
    computer = Server()
    while True:
        x = computer.receive_data()
        if x != "no data within listening time":
            print(x)
            computer.send_update(123321)  # placeholder
            break

def load_test():
    base_station = Server()
    counter = 0
    while True:
        x = base_station.receive_data()
        if x == "test over":
            break
        if x != "no data within listening time":
            counter += 1
            base_station.send_update(counter)

if __name__ == "__main__":
    load_test()