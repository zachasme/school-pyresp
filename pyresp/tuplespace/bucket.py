from . import TupleSpaceNaive


class TupleSpaceBucket(TupleSpaceNaive):

    def __init__(self):
        super().__init__()
        self._tuples = {}

    def _add(self, tuple):
        """Add a tuple, indices, etc."""
        bucket = self._bucket(tuple)
        bucket.append(tuple)

    def _remove(self, tuple):
        """Remove a tuple and any indices"""
        bucket = self._bucket(tuple)
        bucket.remove(tuple)

    def _find(self, pattern):
        """Search tuple space for a pattern"""
        bucket = self._bucket(pattern)
        return next(t for t in bucket if self._match(t, pattern))

    def _bucket(self, sequence):
        """Hash function that computes same hash for tuples and any matching
        pattern
        """
        index = tuple(x if isinstance(x, type) else type(x) for x in sequence)
        try:
            bucket = self._tuples[index]
        except:
            bucket = []
            self._tuples[index] = bucket
        return bucket
