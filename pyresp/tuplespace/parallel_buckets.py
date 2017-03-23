from threading import Thread, Condition, Lock
from . import TupleSpaceBucket
from contextlib import contextmanager
from collections import defaultdict


class TupleSpaceParallelBuckets(TupleSpaceBucket):

    def __init__(self):
        super().__init__()

        #List of the mutation locks for the buckets
        self.mutation_locks_list = defaultdict(list)
        self.mutation_lock_update = Condition()

        #List of the number of readers duing queries in each bucket
        self.readers_list = defaultdict(list)
        self.reader_lock_update = Condition()

        #List of the locks for the number of readers in each bucket
        self.readers_locks_list = defaultdict(list)
        self.readers_lock_list_update = Condition()

        #List of the query locks for each bucket
        self.query_locks_list = defaultdict(list)
        self.query_lock_update = Condition()


    def hash(self,sequence):
        #Hash function - similar to the one used for the buckets
        return tuple(x if isinstance(x, type) else type(x) for x in sequence)


    def put(self, *tuple):
        """Place tuple in tuple space

        Notifies all locks of new tuple.
        """
        with self.mutation_lock(tuple,notify=True), self.query_lock(tuple,notify=True):
                    # run tuple insertion logic while lock is held
                    self._add(tuple)


    def get(self, *pattern, blocking=True):
        """Fetch, remove and return tuple from repository

        If blocking, wait until match. Otherwise, return None.
        """
        while True:
            with self.mutation_lock(pattern):
                try:
                    tuple = self._find(pattern)
                    self._remove(tuple)
                    return tuple
                except:
                    if blocking:
                        self.wait_mutation_lock(pattern)
                    else:
                        return None


    def query(self, *pattern, blocking=True):
        """Find and return tuple, blocks until tuple is available

        Same as atomic version of
        > tuple = get(*pattern)
        > put(tuple)
        > return tuple
        """
        while True:
            #If first reader, get lock
            with self.readers_lock(pattern):
                r = self.addReader(pattern)
                if r == 1:
                    self.get_mutation_lock(pattern)
            try:
                wait = False  # must be reset to False on each iteration
                return self._find(pattern)
            except:
                if not blocking:
                    return None
                else:
                    wait = True  # ensure block after query update
            finally:
            #If last reader, release lock
                with self.query_lock(pattern):
                    with self.readers_lock(pattern):
                        r = self.removeReader(pattern)
                        if r == 0:
                            self.release_mutation_lock(pattern)
                    if wait:
                        self.wait_query_lock(pattern)


    #Genereal methods for a lock
    def get_lock(self,pattern,list_of_locks,update_lock):
        index = self.hash(pattern)
        with update_lock:
            # creates a new lock, if it does not exist for the given index
            if not list_of_locks[index]:
                list_of_locks[index].append(Condition(lock=Lock()))
        list_of_locks[index][0].acquire()

    def release_lock(self,pattern,list_of_locks,notify=False):
        index = self.hash(pattern)
        if notify:
            list_of_locks[index][0].notify_all()
        list_of_locks[index][0].release()

    def wait_lock(self,pattern,list_of_locks):
        list_of_locks[self.hash(pattern)][0].wait()


    #Methods for managing the mutation locks
    @contextmanager
    def mutation_lock(self,pattern,notify=False):
        self.get_lock(pattern, self.mutation_locks_list, self.mutation_lock_update)
        try:
            yield
        finally:
            self.release_lock(pattern, self.mutation_locks_list,notify=notify)

    def get_mutation_lock(self,pattern):
        self.get_lock(pattern,self.mutation_locks_list,self.mutation_lock_update)

    def release_mutation_lock(self,pattern,notify=False):
        self.release_lock(pattern,self.mutation_locks_list,notify=notify)

    def wait_mutation_lock(self,pattern):
        self.wait_lock(pattern,self.mutation_locks_list)


    #Methods for managing the query locks
    @contextmanager
    def query_lock(self,pattern,notify=False):
        self.get_lock(pattern, self.query_locks_list, self.query_lock_update)
        try:
            yield
        finally:
            self.release_lock(pattern, self.query_locks_list,notify=notify)

    def wait_query_lock(self,pattern):
        self.wait_lock(pattern,self.query_locks_list)

    #Methods for updating the number of readers in each bucket
    @contextmanager
    def readers_lock(self,pattern):
        self.get_lock(pattern,self.readers_locks_list,self.readers_lock_list_update)
        try:
            yield
        finally:
            self.release_lock(pattern, self.readers_locks_list)

    def addReader(self,pattern):
        index = self.hash(pattern)
        with self.reader_lock_update:
            if not self.readers_list[index]:
                self.readers_list[index].append(0)
        self.readers_list[index][0] += 1
        return self.readers_list[index][0]

    def removeReader(self,pattern):
        index = self.hash(pattern)
        self.readers_list[index][0] -= 1
        return self.readers_list[index][0]
