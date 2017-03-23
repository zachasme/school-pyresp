from pyresp import Node, join_agents

# agents
def pinger(owner, other):
  while True:
    other.put("PING")
    owner.get("PONG")

def ponger(owner, other):
  while True:
    owner.get("PING")
    other.put("PONG")

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
