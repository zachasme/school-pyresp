from threading import Thread, Condition


class TupleSpaceNaive:
    """Provides a repository of tuples that can be accessed concurrently."""

    def __init__(self):
        self._tuples = []
        self._mutation_lock = Condition()

    def put(self, *tuple):
        """Place tuple in repository."""
        with self._mutation_lock:
            self._add(tuple)
            self._mutation_lock.notify_all()

    def get(self, *pattern, blocking=True):
        """Fetch, remove and return tuple from repository

        If blocking, wait until match. Otherwise, return None.
        """
        while True:  # the loop is escaped on first iteration when not blocking
            with self._mutation_lock:
                try:
                    tuple = self._find(pattern)
                    self._remove(tuple)
                    return tuple
                except:
                    if blocking:
                        self._mutation_lock.wait()
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
            with self._mutation_lock:
                try:
                    return self._find(pattern)
                except:
                    if not blocking:
                        return None
                self._mutation_lock.wait()

    def putp(self, *tuple):
        """Non-blocking put."""
        Thread(target=self.put, args=tuple).start()

    def getp(self, *pattern):
        """Non-blocking get."""
        return self.get(*pattern, blocking=False)

    def queryp(self, *pattern):
        """Non-blocking query."""
        return self.query(*pattern, blocking=False)

    def _add(self, tuple):
        """Add a tuple, indices, etc."""
        self._tuples.append(tuple)

    def _remove(self, tuple):
        """Remove a tuple and any indices"""
        self._tuples.remove(tuple)

    def _find(self, pattern):
        """Search tuple space for a pattern"""
        return next(t for t in self._tuples if self._match(t, pattern))

    def _match(self, thing, pattern):
        """Determine if thing matches pattern

        Works by recursively checking elements if thing is a sequence.
        """
        # pattern is a python type
        if isinstance(pattern, type):
            return isinstance(thing, pattern)

        # if sequence, then recursively check
        try:
            # ensure sequences of same length (and not string)
            if not isinstance(pattern, str) and len(thing) == len(pattern):
                # recursively check each pair
                return all(self._match(*pair) for pair in zip(thing, pattern))
        except:
            # probably exception from calling len() on non-sequence
            pass

        # direct match using python equality
        return thing == pattern
