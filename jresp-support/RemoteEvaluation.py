from pyresp.jresp import Listener
from pyresp import Node, join_agents
import time

# Client Node!
LOCAL = '127.0.0.1'
SERVERPORT = 9999
THISPORT = 9000
CLIENTNAME = 'pyRESP client'

def client(owner, listener):
    for num in range(0,10):
        # init link to the server
        server = listener.link((LOCAL, SERVERPORT), 'server')

        # request a computation of factorial(n)
        print('"{}" sending request to compute fact({})...'.format(CLIENTNAME,num))
        server.put('run', num, 'for', CLIENTNAME)

        # retrieve address for the sandbox and init a link to it
        print('"{}" getting sandbox address...'.format(CLIENTNAME))
        sandboxT = owner.get('sandbox', str)
        print('Got sandbox name {}'.format(sandboxT[1]))
        sandbox = listener.link((LOCAL, SERVERPORT), sandboxT[1])

        # get the result which the server put in the sandbox
        print('"{}" getting result'.format(CLIENTNAME))
        result = sandbox.get(('result', int))
        print('"{}" got result "{}"'.format(CLIENTNAME, result))

        # delay next iteratin by 2 seconds, used for the presentation
        time.sleep(2)


if __name__ == '__main__':
    node = Node(CLIENTNAME)
    listener = Listener(node, (LOCAL, THISPORT))

    node.add(client, listener)
    node.start()

    join_agents()
