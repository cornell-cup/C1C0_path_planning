import socket


class Network(object):
    def __init__(self):
        self.port = 4000
        # TODO: HARD CODED SERVER IP! '192.168.86.83'
        self.server = (self.get_ip(), 4000)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @staticmethod
    def get_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ipv4 = s.getsockname()[0]
        except Exception:
            ipv4 = '127.0.0.1'
        finally:
            s.close()
        print(ipv4)
        return ipv4
