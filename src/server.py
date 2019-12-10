#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}:  {content}"
            self.factory.messages.append(content.encode())
            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:

            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                if self.login in self.factory.nicknames:
                    self.sendLine("Login used, try another".encode())
                    self.transport.loseConnection()
                else:
                    self.factory.nicknames.append(self.login)
                    self.sendLine("Welcome!".encode())
                    self.send_history()
            else:
                self.sendLine("Invalid login".encode())

    def send_history(self):
        if len(self.factory.messages) == 0:
            return
        elif len(self.factory.messages) < 11:
            for item in self.factory.messages:
                self.sendLine(item)
        else:
            i = len(self.factory.messages) - 10
            while i < len(self.factory.messages):
                self.sendLine(self.factory.messages[i])
                i += 1


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    nicknames: list
    messages: list

    def startFactory(self):
        self.clients = []
        self.nicknames = []
        self.messages = []
        print("Server started")

    def stopFactory(self):
        print("Server stopped")


reactor.listenTCP(1234, Server())
reactor.run()
