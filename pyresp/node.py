from threading import Thread
from uuid import uuid4

from pyresp.tuplespace import TupleSpaceBucketConcurrentQuery


class Node:
    """Holds a single tuple space, as well as added agents."""

    def __init__(self, name=None, TupleSpace=TupleSpaceBucketConcurrentQuery):
        self.threads = []

        # generate unique name unless human-friendly one is given
        self.name = name if name is not None else uuid4()

        # initialize empty tuple space
        self.tuplespace = TupleSpace()

    def __getattr__(self, name):
        """Proxy tuple space methods"""
        return getattr(self.tuplespace, name)

    def add(self, agent, *args):
        """Add agent to Node

        Agents must be started using node.start()

        Agent must be a callable
        """
        # agent always recieves owner node as first argument
        agent_args = (self,) + args

        thread = Thread(target=agent, args=agent_args)
        # marking thread as daemon will kill it when main process terminates
        # see https://docs.python.org/3/library/threading.html#thread-objects
        thread.daemon = True

        # store the thread for it to be started later
        self.threads.append(thread)

    def start(self):
        """Start all threads (agents, listeners, etc.)"""
        for thread in self.threads:
            thread.start()
