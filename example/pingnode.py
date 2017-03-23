import logging
from threading import Thread
logging.basicConfig(level=logging.DEBUG)
from multiprocessing import Process
import socket
import time
import functools
import json
import pickle

from pyresp import Node, join_agents
from pyresp.virtual import connection

STOP_BYTE = b'+'
BUFFER_SIZE = 1

def recv(socket):
    recv_byte = socket.recv(1)
    message = b""

    # recieve data one byte at a time
    while not recv_byte == STOP_BYTE:
        message += recv_byte
        recv_byte = socket.recv(1)

    return pickle.loads(message)


def send(socket, *msg):
    serialized = pickle.dumps(msg) + STOP_BYTE
    socket.sendall(serialized)

def listener(host, port, owner):
    """This is the node-facing part

    It listens to a connecting agent
    """
    # listen for connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print('listening at', host, port)
        # accept connection
        conn, addr = s.accept()
        print('got conn', addr)
        with conn:
            while True:
                cmd, argument = recv(conn)

                # only allow tuple space operations
                if cmd not in ['put', 'putp', 'get', 'getp', 'query', 'queryp']:
                    continue

                # handle operation
                operation = getattr(owner, cmd)
                result = operation(*argument)
                send(conn, result)


class Link:
    """This is the agent-facing part, provides tuplespace methods that simply
    proxy to the remote node
    """

    TIMEOUT_BASE = 1.6

    def __init__(self, host, port, name, serializer=None):
        self.serializer = serializer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('gon try connects')
        # wait for connection
        self.connect(host, port)
        print('great success')

    def connect(self, host, port):
        timeouts = 0
        while True:
            try:
                print('Tryna connect', host, port)
                self.socket.connect((host, port))
                break
            except Exception as e: # exponetial sleep on connection error
                print(e)
                timeouts += 1
                time.sleep(self.TIMEOUT_BASE ** timeouts)

    def put(self, *tuple):
        print('puttin')
        send(self.socket, 'put', tuple)
        print(' put mid')
        self.socket.close()
        x = recv(self.socket) # block until acknowledged
        print('put done', x)

    def get(self, *pattern):
        send(self.socket, 'get', pattern)
        tuple = recv(self.socket)
        return tuple

















def pinger(owner, remote_ip, remote_port):
    other = Link(remote_ip, remote_port, "remote name")

    print("agent {} starts...".format(owner.name))
    while True:
        print("PING!")
        other.put("PING")
        print("PING DONE!")
        owner.get("PONG")
        print("GET PONG!")

local_port = 9998
remote_port = 9999
local_ip = '127.0.0.1'
remote_ip = '127.0.0.1'

if __name__ == '__main__':
    partlistener = functools.partial(listener, local_ip, local_port)

    n = Node()
    n.add(partlistener)
    n.add(pinger, remote_ip, remote_port)
    n.start()
    join_agents()
