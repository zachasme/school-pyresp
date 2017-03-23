import unittest
import json
from pyresp.jresp.socketport import SocketPort

class TestMessageClass(unittest.TestCase):
    def test_newmessage_put(self):
        local = ('localhost', 9999)
        remote = ('localhost', 9999)

        sp = SocketPort(local, 'ping', remote, 'pong')
        type = 'PUT_REQUEST'
        src = {'name':'ping','host':'localhost','port':9999}
        target = 'pong'
        data = ('PING',)

        # read in JSON object from file
        ack_json = './json/PUT.json'
        f = open(ack_json, 'r')
        read = json.loads(f.read())
        f.close()

        # create message and set session
        msg = sp._new_message(type, target, data)
        msg['session'] = 0

        print(msg)
        print(read)

        self.assertTrue(msg == read)

    def test_newmessage_put(self):
        local = ('localhost', 9999)
        remote = ('localhost', 9998)

        sp = SocketPort(local, 'ping', remote, 'pong')
        type = 'TUPLE_REPLY'
        src = {'name':'pong','host':'localhost','port':9998}
        target = 'ping'
        data = ('test',)

        # read in JSON object from file
        ack_json = './json/TUPLE_REPLY.json'
        f = open(ack_json, 'r')
        read = json.loads(f.read())
        f.close()

        # create message and set session
        msg = sp._new_message(type, target, data)
        msg['session'] = 0

        self.assertTrue(msg == read)

    def test_newmessage_get1(self):
        local = ('localhost', 9999)
        remote = ('localhost', 9998)

        sp = SocketPort(local, 'ping', remote, 'pong')
        type = 'GET_REQUEST'
        src = {'name':'pong','host':'localhost','port':9998}
        target = 'ping'
        data = ('PING',)

        # read in JSON object from file
        ack_json = './json/GET-1.json'
        f = open(ack_json, 'r')
        read = json.loads(f.read())
        f.close()

        # create message and set session
        msg = sp._new_message(type, target, data)
        msg['session'] = 1

        self.assertTrue(msg == read)

    def test_newmessage_get2(self):
        local = ('localhost', 9999)
        remote = ('localhost', 9998)

        sp = SocketPort(local, 'ping', remote, 'pong')
        type = 'GET_REQUEST'
        src = {'name':'pong','host':'localhost','port':9998}
        target = 'ping'
        data = (12321321,str)

        # read in JSON object from file
        ack_json = './json/GET-2.json'
        f = open(ack_json, 'r')
        read = json.loads(f.read())
        f.close()

        # create message and set session
        msg = sp._new_message(type, target, data)
        msg['session'] = 1

        self.assertTrue(msg == read)

    def test_newmessage_fail(self):
        local = ('localhost', 9999)
        remote = ('localhost', 9998)

        sp = SocketPort(local, 'ping', remote, 'pong')
        type = 'FAIL'
        src = {'host':'localhost','port':9998}
        target = 'ping'

        data = 'Node blah is unknown at socket:/127.0.0.1:9998'

        # read in JSON object from file
        ack_json = './json/FAIL.json'
        f = open(ack_json, 'r')
        read = json.loads(f.read())
        f.close()

        # create message and set session
        msg = sp._new_message(type, target, data)
        msg['session'] = 0

        print(msg)
        print(read)

        self.assertTrue(msg == read)

    def test_newmessage_ack(self):
        local = ('localhost', 9999)
        remote = ('localhost', 9998)

        sp = SocketPort(local, 'ping', remote, 'pong')
        type = 'ACK'
        src = {'name':'ping','host':'localhost','port':9999}
        target = 'pong'
        # FIXME: data field should be a tuple in this case
        dict = [{'type':'java.lang.String','value':'PING'}]


        # read in JSON object from file
        ack_json = './json/ACK.json'
        f = open(ack_json, 'r')
        read = json.loads(f.read())
        f.close()

        # create message and set session
        msg = sp._new_message(type, target, None)
        msg['session'] = 0

        self.assertTrue(msg == read)

if __name__ == '__main__':
    unittest.main()
