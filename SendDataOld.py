import socket
import pickle

## client file, for jetson
def Main():
    host = '192.168.86.79'  # client ip
    
    port = 4005
    server = ('192.168.86.79', 4000)

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
    print(socket.gethostbyname(socket.gethostname()))
    Main()