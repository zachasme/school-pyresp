from pyresp.jresp import Link, Listener
from pyresp import Node, join_agents
import logging
logging.basicConfig(level=logging.DEBUG)

LOCAL = ('127.0.0.1', 9999)
REMOTE = ('127.0.0.1', 9998)

TEST_TUPLE = ("PONG", 1,)
TEST_PATTERN = (str, int,)


def pinger(owner, other):
    print("agent {} starts...".format(owner.name))
    while True:
        owner.get(*TEST_PATTERN)
        print("got pong!")
        other.put("PING")
        print("pinged!")


def ponger(owner, other):
    print("agent {} starts...".format(owner.name))
    while True:
        other.put(*TEST_TUPLE)
        print("ponged!")
        owner.get("PING")
        print("got ping!")


if __name__ == '__main__':
    n1 = Node("ping")
    n2 = Node("pong")

    listener1 = Listener(n1, LOCAL)
    listener2 = Listener(n2, REMOTE)
    linktonode2 = listener1.link(REMOTE, "pong")
    linktonode1 = listener2.link(LOCAL, "ping")

    n1.add(pinger, linktonode2)
    n2.add(ponger, linktonode1)

    n1.start()
    n2.start()

    join_agents()
