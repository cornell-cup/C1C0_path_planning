# works

import socket
import pickle

## server file, for external laptop doing path planning calculations
def Main():
    host = '0.0.0.0'  # Server ip
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print("Server Started")
    while True:
        data, addr = s.recvfrom(1024)
        # data = data.decode('utf-8')
        print("Message from: " + str(addr))
        print("From connected user: " + str(data))
        data= pickle.loads(data)
        print("From connected user: " + str(data))
        data = pickle.dumps(data)
        print("Sending: " + str(data))
        s.sendto(data, addr)
    c.close()


if __name__ == '__main__':
    Main()