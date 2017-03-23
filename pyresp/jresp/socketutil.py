import socket
import json
import logging

logging.basicConfig(level=logging.WARNING)

RECIEVE_BUFFER = 1024


def listen(address):
    """ Set up and return a TCP server object """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(address)
    s.listen(1)
    logging.info('Bound to address %s', address)
    return s


def chunks(connection):
    """Recieve all chunks from a given connection as a generator"""
    while True:
        chunk = connection.recv(RECIEVE_BUFFER)
        if not chunk:
            return
        yield chunk


def recvjson(connection):
    """ Recieve a JSON object as a byte string, decode and deserialize, returns a
        Python dictionary """
    data = b"".join(chunks(connection))
    logging.info('Recieved JSON object: %s', json.loads(data.decode()))
    return json.loads(data.decode())


def sendjson(target, object):
    """ Serialize object as JSON and send the byte string to the target """
    # initialise connection (`with` keyword ensures socket is closed)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(target)
        # send the dict as a JSON byte string
        data = bytes(json.dumps(object).encode())
        logging.info('Sending object as JSON: %s', object)
        s.sendall(data)
