from threading import Thread, Condition
from . import TupleSpaceBucket, TupleSpaceConcurrentQuery


class TupleSpaceBucketConcurrentQuery(TupleSpaceBucket, TupleSpaceConcurrentQuery):
    pass
