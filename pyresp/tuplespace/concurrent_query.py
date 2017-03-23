from threading import Thread, Condition, Lock
from . import TupleSpaceNaive as TupleSpace


class TupleSpaceConcurrentQuery(TupleSpace):
    """Provides a repository of tuples that can be accessed concurrently

    Synchronization such that:
      * any mutation (get/put/getp/putp) locks the tuple space
      * when no mutation is happening, simultaneous queries is allowed
    """

    def __init__(self):
        super().__init__()

        # locks
        self.mutation_lock = Condition(lock=Lock())
        self.query_lock = Condition()
        self.queries = 0
        self.queries_update = Condition()

    def put(self, *tuple):
        """Place tuple in tuple space

        Notifies all locks of new tuple.
        """
        with self.mutation_lock, self.query_lock:
            # run tuple insertion logic while lock is held
            self._add(tuple)
            self.query_lock.notify_all()
            self.mutation_lock.notify_all()

    def get(self, *pattern, blocking=True):
        """Fetch, remove and return tuple from repository

        If blocking, wait until match. Otherwise, return None.
        """
        while True:  # the loop is escaped on first iteration when not blocking
            with self.mutation_lock:
                try:
                    tuple = self._find(pattern)
                    self._remove(tuple)
                    return tuple
                except:
                    if blocking:
                        self.mutation_lock.wait()
                    else:
                        return None

    def query(self, *pattern, blocking=True):
        """Find and return tuple, blocks until tuple is available

        If blocking, wait until match. Otherwise, return None.

        Same as atomic version of
        > tuple = get(*pattern)
        > put(tuple)
        > return tuple
        """
        while True:  # the loop is escaped on first iteration when not blocking
            with self.queries_update:
                self.queries += 1
                if self.queries == 1:  # first query acquires mutation lock
                    self.mutation_lock.acquire()
            try:
                wait = False  # must be reset to False on each iteration
                return self._find(pattern)
            except:
                if not blocking:
                    return None
                else:
                    wait = True  # ensure block after query update
            finally:
                with self.query_lock:
                    with self.queries_update:
                        # last reader releases mutation lock
                        self.queries -= 1
                        if self.queries == 0:
                            self.mutation_lock.release()
                    if wait:
                        # only reachable if blocking and no tuple was found
                        self.query_lock.wait()
