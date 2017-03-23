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

def recv(socket):
    recv_byte = socket.recv(1)
    message = b""

    # recieve data one byte at a time
    while not recv_byte == b'+':
        message += recv_byte
        recv_byte = socket.recv(1)

    return pickle.loads(message)


def send(socket, *msg):
    serialized = pickle.dumps(msg) + b'+'
    socket.sendall(serialized)

def listener(host, port, owner):
    """This is the node-facing part

    It listens to a connecting agent
    """

    print('*** listener starting at ', host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("BINDING", host, port)
    sock.bind((host, port))
    sock.listen(1)
    print('*** listening at ', host, port)

    sc, sockname = sock.accept()
    print('*** connection from ', sockname)

    while True:
        cmd, message = recv(sc)

        if cmd == 'PUT':
            owner.put(*message)
            send(sc, 1)

        if cmd == 'GET':
            t = owner.get(*message)
            send(sc, t)


class Link:
    """This is the agent-facing part, provides tuplespace methods that simply
    proxy to the remote node
    """
    def __init__(self, host, port, name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # wait for connection
        connected = False
        while not connected:
            try:
                sock.connect((host, port))
                connected = True
            except:
                time.sleep(1)
        self.connection = sock

    def put(self, *tuple):
        send(self.connection, 'PUT', tuple)
        #self.connection.send(('PUT', tuple))
        recv(self.connection) # block until acknowledged

    def get(self, *pattern):
        send(self.connection, 'GET', pattern)
        tuple = recv(self.connection)
        return tuple

















def pingpong_process(msgs, ports):
    def pinger(owner, remote_ip, remote_port):
        other = Link(remote_ip, remote_port, "remote name")

        print("agent {} starts...".format(owner.name))
        while True:
            other.put(msgs[0])
            owner.get(msgs[1])
            print(msgs[1])

    local_port = ports[0]
    remote_port = ports[1]
    local_ip = '127.0.0.1'
    remote_ip = '127.0.0.1'

    partlistener = functools.partial(listener, local_ip, local_port)

    n = Node()
    n.add(partlistener)
    n.add(pinger, remote_ip, remote_port)
    n.start()
    join_agents()

if __name__ == '__main__':

    Process(target=pingpong_process, args=(["ping", "pong"], [8000, 8001])).start()
    Process(target=pingpong_process, args=(["pong", "ping"], [8001, 8000])).start()
