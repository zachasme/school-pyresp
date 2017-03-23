# This is a pyRESP version of the PING client from RemotePingPong.java
from pyresp.jresp import Listener
from pyresp import Node, join_agents

LOCAL = '127.0.0.1'
PINGPORT = 9999
PONGPORT = 9998

def pingnode(owner, other):
    while True:
        print('PING!')
        other.put('PING')
        print('PING DONE!')
        owner.get('PONG')
        print('GOT PONG!')

if __name__ == '__main__':
    node = Node('ping')
    listener = Listener(node, (LOCAL, PINGPORT))
    link = listener.link((LOCAL, PONGPORT), 'pong')

    node.add(pingnode, link)
    node.start()

    join_agents()
