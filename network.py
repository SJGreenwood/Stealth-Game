import socket

class Network():
    """A class that connects a client to the server"""
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 1024
        self.address = (self.server, self.port)
        self.info = self.connect()

    def connect(self):
        try:
            # Connect to the client and get the position of the player
            self.client.connect(self.address)
            return self.client.recv(2048).decode()
        except Exception:
            pass

    def send(self, data):
        """Send messages to the server"""
        try:
            self.client.send((data).encode())
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)