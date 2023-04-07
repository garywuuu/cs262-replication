import clientg as c
import serverg as s

import grpc
import time
from concurrent import futures

import chat_pb2 as chat
import chat_pb2_grpc as rpc

address = 'localhost'
port = 11912

usr1 = "aaa"
usr2 = "bbb"
usr3 = "cc"

class Test:
    def __init__(self):
        self.hi = "hi"

    def test_signup(self):
        r1 = self.c1.signup(usr1)
        assert r1.success         

        r2 = self.c2.signup(usr2)
        assert r2.success

        # duplicate existing user
        r3 = self.c3.signup(usr1)
        assert not r3.success

        print("PASSED: signup")

    def test_logout(self):
        r1 = self.c1.logout()
        assert r1.success

        r2 = self.c2.logout()
        assert r2.success

        print("PASSED: logout")

    def test_login(self):
        r1 = self.c1.login(usr1)
        assert r1.success

        r2 = self.c2.login(usr2)
        assert r2.success

        # duplicate active user
        r3 = self.c3.login(usr1)
        assert not r3.success

        # nonexistent user
        r4 = self.c3.login("xyz")
        assert not r4.success

        print("PASSED: login")

    def test_list(self):
        r1 = self.c1.list("")
        assert r1.success

        r1 = self.c1.list(usr2)
        assert r1.success

        print("PASSED: list")

    def test_send(self):
        r1 = self.c1.send(usr2, "hi")
        assert r1.success

        r2 = self.c3.send(usr1,"bye")
        assert r2.success

        # add automated testing for undelivered

    def test_delete(self):
        r1 = self.c1.delete()
        assert r1.success

        # can now signup with deleted acct
        r2 = self.c1.signup(usr1)
        assert r2.success


if __name__ == '__main__':
    try:
        t = Test()
        serverobj = s.ChatServer()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
        rpc.add_ChatServerServicer_to_server(serverobj, server)  # register the server to gRPC
        print('Starting server. Listening...')
        server.add_insecure_port('[::]:' + str(port))
        server.start()

        t.c1 = c.Client()
        t.c2 = c.Client()
        t.c3 = c.Client()

        t.test_signup()
        t.test_logout()
        t.test_login()
        t.test_list()
        t.test_send()
        t.test_delete()

        server.stop(None)

    except KeyboardInterrupt:
        server.stop(None)
