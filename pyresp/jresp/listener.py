# TCP Client/Server application for communication with jRESP Nodes.

import logging
from threading import Thread
from . import serialization
from . import socketutil
from .link import Link


class Listener(Thread):
    """A TCP server which listens for tuple space requests sent as JSON.
    """

    def __init__(self, node, local_address):
        super().__init__()
        self.address = local_address
        self.tuplespace = node
        self.nodename = node.name
        self.socket = socketutil.listen(self.address)

        self.links = []
        self.daemon = True
        self.start()

    def run(self):
        """Called when thread starts

        Continually accepts sockets connections, which are separate requests,
        and processes them one at a time.

        Uses the type parameter to call appropriate handler method.
        """
        while True:
            connection, address = self.socket.accept()
            with connection:
                request = socketutil.recvjson(connection)

            type = request['type'].lower()
            target = (request['source']['address']['host'],
                      request['source']['address']['port'])

            # call appropriate request handler
            handler = getattr(self, "_handle_{}".format(type))
            response = handler(request)
            logging.info("handling %s with response %s", request, response)

            # and send response
            if response:
                socketutil.sendjson(target, response)

    def _handle_put_request(self, request):
        """Puts given tuple into owners tuple space then sends ACK."""
        tuple = serialization.load_tuple(request['tuple'])
        self.tuplespace.put(*tuple)
        return self._acknowledge(request)

    def _handle_get_request(self, request):
        return self._handle_retrieve_request(request, 'get')

    def _handle_query_request(self, request):
        return self._handle_retrieve_request(request, 'query')

    def _handle_retrieve_request(self, request, operation):
        """Performs requested retrieval operation, then sends result."""
        pattern = serialization.load_template(request['template'])
        tuple = getattr(self.tuplespace, operation)(*pattern)
        javatuple = serialization.dump_tuple(tuple)

        response = self._new_message(request)
        response['type'] = 'TUPLE_REPLY'
        response['tuple'] = javatuple

        return response

    def _handle_tuple_reply(self, message):
        self._wake_links(message)

    def _handle_ack(self, message):
        self._wake_links(message)

    def _wake_links(self, message):
        """Wake up all links created for this listener.

        They might be waiting for ACKs for TUPLE_REPLYs"""
        for link in self.links:
            link.wake(message)

    def _handle_fail(self, request):
        """Handles errors from remote node."""
        raise Exception(request['message'])

    def _acknowledge(self, request):
        """Sends an ACK response."""
        response = self._new_message(request)
        response['type'] = 'ACK'

        return response

    def _new_message(self, request):
        """Creates a new message template."""
        host, port = self.address
        return {
            'target': request['source']['name'],
            'session': request['session'],
            'source': {
                'name': self.nodename,
                'address': {
                    'host': host,
                    'port': port,
                    'addressCode': 'socket',
                }
            }
        }

    def link(self, remote_address, remote_name):
        """Make a new link for use in agent"""
        link = Link(self.address, self.nodename, remote_address, remote_name)
        self.links.append(link)
        return link
