from .node import Node

from time import sleep
from threading import active_count


def join_agents():
    """Wait for all threads to finish

    For now we just sleep to keep main thread alive
    this way it can still catch ctrl+c
    """
    while active_count() > 1:
        sleep(1)
