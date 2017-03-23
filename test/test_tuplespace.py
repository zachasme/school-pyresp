import pytest
from threading import Thread
from time import time, sleep

from pyresp.tuplespace import (
    TupleSpaceNaive, TupleSpaceBucket,
    TupleSpaceConcurrentQuery, TupleSpaceBucketConcurrentQuery,
    TupleSpaceParallelBuckets
)

BLOCK_TEST_TIME = 0.1
TUPLE = ("foo", 1, (0, .5, 1, "baz"), "bar")
PATTERN = (str, int, (int, float, int, str), str)


"""FIXTURES"""


@pytest.fixture(params=[TupleSpaceNaive, TupleSpaceBucket,
                        TupleSpaceConcurrentQuery,
                        TupleSpaceParallelBuckets])
def TupleSpaceImplementation(request):
    return request.param


@pytest.fixture
def ts(TupleSpaceImplementation):
    ts = TupleSpaceImplementation()
    return ts


@pytest.fixture(params=['get', 'getp', 'query', 'queryp'])
def collector(ts, request):
    """fixture for collector operations"""
    return getattr(ts, request.param)


@pytest.fixture(params=['getp', 'queryp'])
def nonblocking_collector(ts, request):
    return getattr(ts, request.param)


@pytest.fixture(params=['get', 'query'])
def blocking_collector(ts, request):
    return getattr(ts, request.param)


@pytest.fixture(params=['get', 'getp'])
def destructive_collector(ts, request):
    return getattr(ts, request.param)


"""TESTS"""


@pytest.mark.parametrize("tuple, pattern", [
    (1, 1),
    (.1, float),
    (1, int),
    ("foo", "foo"),
    ("foo", str),
    ((1,), tuple),
    ((1, 2), (1, int)),
    (
        ("foo", 1, (0, .5, 1, "baz"), "bar"),
        (str, int, (int, float, int, str), str)
    ),
    (
        ("foo", 1, (0, .5, 1, "baz"), "bar"),
        (str, 1, (int, float, 1, "baz"), "bar")
    ),
])
def test_true_match(ts, tuple, pattern):
    """Test matching logic"""
    assert ts._match(tuple, pattern)


@pytest.mark.parametrize("tuple, pattern", [
    (1, 2),
    ("foo", "bar"),
    (1, str),
    ("foo", int),
    (("foo", 1), (str, str)),
])
def test_false_match(ts, tuple, pattern):
    """Test matching logic for false matches"""
    assert not ts._match(tuple, pattern)


def test_putp(ts):
    """Tuple from putp should eventually end up in tuple space"""
    ts.putp(*TUPLE)
    assert ts.get(*PATTERN) == TUPLE


def test_found(ts, collector):
    """should return tuple matching mixed pattern"""
    ts.put(*TUPLE)
    assert collector(*PATTERN) == TUPLE


def test_nonblocking_none(nonblocking_collector):
    """should return None when pattern is not in tuple space"""
    assert nonblocking_collector(*PATTERN) is None


def test_nonblocking_delayed_put(ts, nonblocking_collector):
    """should return None even if tuple is added later"""
    def thread():
        sleep(BLOCK_TEST_TIME)
        ts.put(*TUPLE)

    Thread(target=thread).start()
    assert nonblocking_collector(*PATTERN) is None


def test_blocking_blocks(blocking_collector):
    """should block forever if tuple is not added"""
    def thread():
        blocking_collector(*PATTERN)

    t = Thread(target=thread)
    t.daemon = True
    start = time()
    t.start()
    t.join(BLOCK_TEST_TIME)

    assert time() - start >= BLOCK_TEST_TIME


def test_blocking_delayed_found(ts, blocking_collector):
    """should return tuple matching pattern after blocking wait"""
    def thread():
        sleep(BLOCK_TEST_TIME)
        ts.put(*TUPLE)

    Thread(target=thread).start()

    assert blocking_collector(*PATTERN) == TUPLE


def test_removal(ts, destructive_collector):
    """Should remove tuple when found"""
    ts.put(*TUPLE)
    assert not ts.queryp(*TUPLE) is None
    destructive_collector(*TUPLE)
    assert ts.queryp(*TUPLE) is None
