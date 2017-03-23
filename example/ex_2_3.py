import logging
logging.basicConfig(level=logging.DEBUG)
import time
from pyresp import Node, join_agents

# templates
leaderT = ("leader", str)
voteT = ("vote", str, str)

def elector(home, next):
    print("{} voting for himself...".format(home.name))
    next.put("vote", home.name, home.name)
    t = home.get(*leaderT)
    leader_name = t[1]
    if leader_name == home.name:
        next.put("stop")
    print("{} thinks that {} is the leader.".format(next.name, leader_name))

def forwarder(home, next):
    leader_name = home.name
    elected = False
    while True:
        t = home.get(*voteT)
        #print("Node HOME got a vote.")

        voter_name = t[1]
        candidate_name = t[2]
        # Forward votes if they were issued by another node
        # updating it according to lexicographical order
        if not voter_name == home.name:
            leader_name = leader_name if leader_name > candidate_name else candidate_name
            #print("Node {} forwards a vote from {} to {} for {}...".format(home.name, voter_name, next.name, leader_name))
            next.put("vote", voter_name, leader_name)
        # Otherwise let the elector know who is the leader
        else:
            elected = True
            home.put("leader", leader_name)
    print("node {} stops".format(home.name))


if __name__ == '__main__':
    N = 3
    nodes = [Node("node{}".format(i)) for i in range(N)]

    for (node, next) in zip(nodes, nodes[1:] + [nodes[1]]):
        node.add(elector, next)
        node.add(forwarder, next)

    for node in nodes:
        node.start()

    join_agents()
