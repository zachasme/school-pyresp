from threading import Condition
from . import serialization
from . import socketutil


class Link:
    """Given to agents such that they can contact remote nodes.

    Act as a sort of proxy node: It works just like a Node, but any operations
    are translated into a socket transmission and blocks until the remote
    node responds.

    These should not be instantiated directly, but rather through a Listener:
    > link = listener.link(REMOTE_NODE_ADDRESS, REMOTE_NODE_NAME)
    for example:
    > link = listener.link(('127.0.0.1', 9999), "foo")

    Works with jResp compatible listeners
    (including this implementation itself).
    """

    def __init__(self, local_address, local_name, remote_address, remote_name):
        self.remote_address = remote_address
        self.remote_name = remote_name
        self.lock = Condition()

        self._last_response = {'session': -1}
        self.session = 0

        source_host, source_port = local_address
        self.source = {
            'name': local_name,
            'address': {
                'host': source_host,
                'port': source_port,
                'addressCode': 'socket',
            }
        }

    def put(self, *tuple):
        """Send a put request to target.

        Blocks until request is acknowledged by target.
        """
        request = self._new_request()
        request['type'] = 'PUT_REQUEST'
        request['tuple'] = serialization.dump_tuple(tuple)

        socketutil.sendjson(self.remote_address, request)
        self._await_response()  # wait for but do not use ACK message

    def get(self, *args):
        return self._collect('GET_REQUEST', *args)

    def query(self, *args):
        return self._collect('QUERY_REQUEST', *args)

    def getp(self, *args):
        raise Exception("Operation getp not supported by jResp")

    def queryp(self, *args):
        raise Exception("Operation queryp not supported by jResp")

    def _collect(self, type, tuple):
        """Generic collect operation (used by get/query)

        Blocks until target responds with a TUPLE_REPLY.
        """
        request = self._new_request()
        request['type'] = type
        request['template'] = serialization.dump_template(tuple)

        socketutil.sendjson(self.remote_address, request)

        response = self._await_response()
        return serialization.load_tuple(response['tuple'])

    def wake(self, response):
        """Wake up link with new response.

        This will make thread check if awaited response has arrived, and if so
        continue processing, otherwise go back to waiting."""
        with self.lock:
            self._last_response = response
            self.lock.notify()

    def _await_response(self):
        """Waits for listeners to recieve response

        Only continues when response corresponding to last request arrives.
        """
        with self.lock:
            while self.session != self._last_response['session']:
                self.lock.wait()
            return self._last_response

    def _new_request(self):
        """Creates a fresh request template.

        Also increments session!
        """
        self.session += 1
        return {
            'target': self.remote_name,
            'session': self.session,
            'source': self.source,
        }
