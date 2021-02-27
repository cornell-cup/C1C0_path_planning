import socket
import pickle

## client file, for jetson
def Main():
    host = '10.48.70.249'  # client ip
    port = 4005

    server = ('10.48.70.249', 4000)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    x=[2,3]

    message = input("-> ")
    while message != 'q':
        s.sendto(pickle.dumps(x), server)
        data, addr = s.recvfrom(1024)
        # data = data.decode('utf-8')
        print("Received from server: " + str(pickle.loads(data)))
        message = input("-> ")

        try:
            x.append(int(message))
        except:
            pass
    s.close()


if __name__ == '__main__':
    Main()