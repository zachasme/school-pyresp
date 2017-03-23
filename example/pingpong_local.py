import logging
logging.basicConfig(level=logging.DEBUG)

from pyresp import Node, join_agents

def pinger(owner, other):
    print("pinger starts...")
    while True:
        other.put("ping")
        owner.get("pong")
        print("PONG")

def ponger(owner, other):
    print("ponger starts...")
    while True:
        owner.get("ping")
        print("PING")
        other.put("pong")

if __name__ == '__main__':
    n1 = Node("ping node")
    n2 = Node("pong node")
    n1.add(pinger, n2)
    n2.add(ponger, n1)
    n1.start()
    n2.start()

    join_agents()
