from pyresp.jresp import  Listener
from pyresp import Node, join_agents
import logging
logging.basicConfig(level=logging.DEBUG)

LOCAL = ('127.0.0.1', 9999)
REMOTE = ('127.0.0.1', 9998)

TEST_TUPLE = ("PONG", 1,)
TEST_PATTERN = (str, int,)


def pinger(owner, other):
    #other = Link(owner, other_address, other_name)
    print("agent {} starts...".format(owner.name))
    while True:
        other.put("PING")
        print("putted ping!")
        owner.get("PONG")
        print("PONG!")


def ponger(owner, other):
    print("agent {} starts...".format(owner.name))
    while True:
        owner.get("PING")
        print("PING!")
        other.put("PONG")
        print("putted pong!")


if __name__ == '__main__':

    n1 = Node("ping")  # local
    n2 = Node("pong")  # remote

    listener1 = Listener(n1, LOCAL)  # ping
    listener2 = Listener(n2, REMOTE)  # pong

    n1.add(pinger, listener1.link(REMOTE, "pong"))
    n2.add(ponger, listener2.link(LOCAL, "ping"))

    n1.start()
    n2.start()
    join_agents()
