import socket
from _thread import *

from json import loads, dumps

from game import Game
from sprites import *

def readInfo(positions) -> list:
    """A function that turns a string into a list"""

    return loads(positions)

def makeInfo(positions) -> str:
    """A function that turns a list into a string"""

    return dumps(positions)

def fillDictionary(focus, spriteImage, pos, angle) -> dict:
    return {
        "focus": focus,
        "image": spriteImage,
        "position": pos,
        "angle": angle,
    }

class Server():
    def __init__(self):
        self.host = "127.0.0.1"# "127.0.0.1"  # Standard loopback interface address (localhost)
        self.port = 1024  # Port to listen on (non-privileged ports are > 1023)

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        print(f"Hostname: {hostname}, IP: {ip}")

        self.threadCount = 0

        self.acceptingNewConnections = True

        self.players = []

        self.game = Game()

        start_new_thread(self.runGame, ())

        # Start accepting users
        self.startAccepting()

    def runGame(self):
        while True:
            self.game.new()
            self.game.run()

    def collectSpriteInfo(self, focus):
        infoList = []

        # Add all characters
        for sprite in self.game.all_characters:
            infoList.append(fillDictionary(sprite is focus, f"{sprite.characterName}_{sprite.imageKey}", list(sprite.rect.topleft), sprite.angle))

        # Add all moveable objects
        for sprite in self.game.all_sprites:
            if isinstance(sprite, (Object, Bullet)):
                infoList.append(fillDictionary(False, sprite.imageName, list(sprite.rect.topleft), sprite.angle))

        return infoList

    def startAccepting(self):
        # Create a socket stream
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            # Start listening for connections
            s.listen()
            while self.acceptingNewConnections:
                print("Waiting for connection")
                # Accept new connections
                conn, addr = s.accept()
                print(f"Connected to: {addr[0]}:{addr[1]}")

                # Start replying to their requests
                start_new_thread(self.threaded_client, (conn, self.threadCount))
                self.threadCount += 1
                print(f"Started thread number: {self.threadCount}")

    def threaded_client(self, connection, userIndex):
        """Recieves position updates from players and sends back positions of other users"""

        self.players.append(Player(self.game, self.game.spawnPoint, self.game.characterImgs))
        
        # Make a connection to the client
        connection.send(makeInfo(fillDictionary(True, f"{self.players[userIndex].characterName}_{self.players[userIndex].imageKey}", list(self.players[userIndex].rect.topleft), self.players[userIndex].angle)).encode())
        while True:
            try:
                # Decode the coordinates sent by the client
                keyPresses = readInfo(connection.recv(2048).decode())
                # Send key inputs to the client's player
                self.players[userIndex].get_input(keyPresses)

                if not keyPresses:
                    print("Disconected")
                    break
                else:
                    reply = makeInfo(self.collectSpriteInfo(self.players[userIndex]))

                # Send the reply
                connection.sendall(reply.encode())

            except Exception as e:
                print(e)
                break

        print("Lost connection")
        connection.close()

if __name__ == "__main__":
    s = Server()