import socket, pickle

class SendData:
    def __init__(self):
        external_server= '10.48.70.249'
        self.server = (external_server, 4000)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', 4005))
        self.socket.listen(5)

    def send_data(self, data):
        """sends json-like nested data containing sensor, accelerometer, etc.
        """
        self.socket.sendto(pickle.dumps(data), self.server)

### TEST
if __name__ == "__main__":
    sendData = SendData()
    sendData.send_data([[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9],[1,2,3],[4,5,6],[7,8,9]])



# import socket
# import pickle

# ## client file, for jetson
# def Main():
#     host = '192.168.86.79'  # client ip
#     port = 4005
#     server = ('10.48.70.249', 4000)
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.bind((host, port))

#     x=[2,3]

#     message = input("-> ")
#     while message != 'q':
#         s.sendto(pickle.dumps(x), server)
#         data, addr = s.recvfrom(1024)
#         # data = data.decode('utf-8')
#         print("Received from server: " + str(pickle.loads(data)))
#         message = input("-> ")

#         try:
#             x.append(int(message))
#         except:
#             pass
#     s.close()


# if __name__ == '__main__':
#     Main()

