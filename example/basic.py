from pyresp import Node, join_agents

ITERATIONS = 1000

# agents
def pinger(owner, other):
  for i in range(ITERATIONS):
    other.put("PING")
    owner.get("PONG")
    print("ping", i)

def ponger(owner, other):
  for i in range(ITERATIONS):
    owner.get("PING")
    other.put("PONG")
    print("pong", i)

# nodes
pingnode = Node()
pongnode = Node()

# add agents
pingnode.add(pinger, pongnode)
pongnode.add(ponger, pingnode)

# start nodes
pingnode.start()
pongnode.start()

# keep main thread waiting for agents to terminate
join_agents()
