

import socket
from threading import Event, Lock, Thread
import time
import logging

class Client:

    def __init__(self, host = '', port = 64502, event_listener = None):

        self.host = host
        self.port = port                        # connection info

        self.connection_alive = True
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.msgs = []

    def start_connection(self):

        self.connection_thread = Thread(target=self.start_client)
        self.connection_thread.start()

    def kill(self):

        self.connection_alive = False
        self.client.close()

    def start_client(self):

        self.client.connect((self.host, self.port))
        logging.info('connected')
        while self.connection_alive:

            while len(self.msgs)>0:
                msg = self.msgs.pop()
                print('Try to send:', msg)
                self.client.sendall(bytes(msg, 'utf-8'))

                data = self.client.recv(1)
                print('Response:',data)

            time.sleep(1)


if __name__ == '__main__':


    client = Client(host='', port=65502)
    client.start_connection()

    while True:

        msg = input()
        if msg != '':

            client.msgs.append(msg)

        if msg == 'exit':
            client.kill()
            break

    client.kill()
