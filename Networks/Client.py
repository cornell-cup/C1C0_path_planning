import pickle
from Network import *
from SensorCode.SensorState import *
import sys
import json


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


class Client(Network):
    def __init__(self):
        super().__init__()
        # this used to be 4005, make sure to check this
        self.socket.bind((self.get_ip(), 4004))
        # self.socket.settimeout(4)  # interferes with stopping
        self.receive_ID = 0

    def init_send_data(self, data):
        """
        initial send that requires a confirmation to move on
        """
        x = pickle.dumps({'data': data})
        self.socket.settimeout(1)
        self.socket.sendto(x, self.server)
        try:
            x = self.socket.recvfrom(4096)
            received = pickle.loads(x[0])
            print(f"initial data received: {received}")
            self.socket.settimeout(None)
        except:
            print("CLIENT SEND FAILED")
            self.init_send_data(data)

    def send_data(self, data):
        """ sends json-like nested data containing sensor, accelerometer, etc.
        """
        x = pickle.dumps({'id': self.receive_ID, 'data': data})
        print("size: ", sys.getsizeof(x))
        print(data)
        self.socket.sendto(x, self.server)

    def listen(self):
        x = ["", ("0.0.0.0", 9999)]
        
            # according to pickle docs you shouldn't unpickle from unknown sources, so we have some validation here
        while x[1] != self.server:
            x = self.socket.recvfrom(4096)
            
        y = pickle.loads(x[0])

        self.receive_ID = y['id']
        return y['content']

# test to make sure that SensorState object is <= 4096 bytes
if __name__ == "__main__":
    robot = Client()
    data_packet = SensorState()
    robot.init_send_data("LETS GO")
