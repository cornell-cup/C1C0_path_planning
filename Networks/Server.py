import pickle
from Networks import *


class Server(Network):
    def __init__(self):
        super().__init__()
        self.socket.bind((self.get_ip(), self.port))
        print("Server Started")
        self.client = ("", 0)
        self.last_sent= None
        self.send_ID = 0

    # def endpoint_recieve(self):
    #     x = self.socket.recvfrom(4096)
    #     self.client = x[1]
    #     self.socket.settimeout(1)  # interferes with stopping on further calls
    #     y = pickle.loads(x[0])
    def receive_data_init(self):
        try:
            x = self.socket.recvfrom(4096)
            y = json.loads(x[0].decode('utf-8'))
            self.client = x[1]
            self.send_update("received!")
            # print(type(y['data']))
            return y['data']
        except socket.timeout: 
            self.send_update("received!")
            self.socket.settimeout(1)
            return self.receive_data_init()


    def receive_data(self):
        try:
            x = self.socket.recvfrom(100000)
            self.client = x[1]
            self.socket.settimeout(1)  # interferes with stopping on further calls
            y = json.loads(x[0].decode("utf-8"))
            if y['id'] != self.send_ID:
                self.send_ID += 1
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
        self.last_sent = update
        self.socket.sendto(json.dumps({'id': self.send_ID, 'content': update}).encode('utf-8'), self.client)


def load_test():
    computer = Server()
    while True:
        x = computer.receive_data()
        computer.send_update("ok")
        if x == "done-over":
            return



# test with Client.py main method
if __name__ == "__main__":
    load_test()
