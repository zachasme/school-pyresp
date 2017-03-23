import logging
from multiprocessing import Pipe
from functools import partial

def connection():
    parent, child = Pipe()
    link = LinkRemote(parent)
    listener = partial(unconnected_listener, child)

    return link, listener

class LinkRemote:
    """
    Provides an API for agents
    This is more like a tuplespace proxy!
    """
    def __init__(self, conn):
        # setup SERVER
        self.connection = conn
        self.name = None

        # fetch node name
        #self.connection.send('NAME')
        #self.name = self.connection.recv()

    def put(self, *tuple):
        self.connection.send(('PUT', tuple))
        self.connection.recv() # block until acknowledged

    def putp(self, *tuple):
        self.connection.send('PUTP', tuple)
        # don't block until acknowledged (?)

    def get(self, *pattern):
        logging.info('gettin %s', pattern)
        self.connection.send(('GET', pattern))
        tuple = self.connection.recv()
        return tuple

    def getp(self, *pattern):
        self.server.send(('GETP', pattern))
        maybetuple = self.server.recv()
        return maybetuple

class Listener:
    def __init__(node):
        pass

def unconnected_listener(connection, owner):
    while True:
        cmd, *msg = connection.recv()
        if (cmd == "PUT"):
            tuple = msg[0]
            owner.put(*tuple)
            connection.send(None)
        if (cmd == "GET"):
            pattern = msg[0]
            t = owner.get(*pattern)
            connection.send(t)
