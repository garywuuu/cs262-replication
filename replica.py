from concurrent import futures
import sqlite3
import grpc
import time
import queue
import fnmatch
import random
import threading


import chat_pb2 as chat
import chat_pb2_grpc as rpc

address = 'localhost'
ports = [2056,3056,4056]

class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self,port):
        self.is_master = False
        self.master = None
        self.port = port
        self.clients = {}
        self.conns = {} # dict of all connections to other servers, key=port

        self.connect()

    # The stream which will be used to send new messages to clients
    def ChatStream(self, request: chat.ConnectRequest, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        recipient = request.recipient
        # infinite loop starts for each client
        while True:
            # Check if recipient is active, if they have queued messages
            if self.clients[recipient]["active"]:
                if self.clients[recipient]["queue"].qsize() > 0: 
                    n = self.clients[recipient]["queue"].get(block=False)
                    # pushes message to queue to send to secondaries
                    servMessage = chat.ServConnectReply()
                    servMessage.port = self.port
                    servMessage.sender = n.sender
                    servMessage.recipient = n.recipient
                    servMessage.message = n.message
                    servMessage.active = n.active
                    for port in self.conns: # add to each connection queue
                        self.conns[port]["queue"].put(servMessage) 
                    yield n 

    def SendMessage(self, request: chat.MessageRequest, context):
        # parse out request
        sender = request.sender
        recipient = request.recipient
        message = request.message
        # create reply object
        n = chat.MessageReply()
        # check if user exists
        if recipient not in self.clients.keys():
            n.success = False
            n.error = "Recipient not found."
        else:
            # regardless of whether user is active, we'll push to queue
            forward = chat.ConnectReply()
            forward.active = True # not disconnecting
            forward.sender = sender
            forward.recipient = recipient
            forward.message = message
            self.clients[recipient]["queue"].put(forward)
            # reply with overall sendMessage success + print debugging statements
            n.success = True
            if self.clients[recipient]["active"]:
                print("Sent: [{} -> {}] {}".format(sender,recipient,message))
            else: 
                print("Queued: [{} -> {}] {}".format(sender,recipient,message))
        return n
    
    def Signup(self, request: chat.SignupRequest, context):
        n = chat.SignupReply()
        username = request.username
        # if user already exists
        if username in self.clients.keys():
            n.success = False
            n.error = "Username already exists."
            print("Signup from {} failed: User already exists.".format(username))
        else:
            # add new user dictionary to client dictionary
            # initiate empty thread-safe queue for msgs
            self.clients[username] = {"active": True, "queue": queue.SimpleQueue()}
            print("New user {} has arrived!".format(username))
            n.success = True
        return n

    def Login(self, request: chat.LoginRequest, context):
        n = chat.LoginReply()
        username = request.username
        # check if user exists
        if username not in self.clients.keys():
            n.success = False
            n.error = "No existing user found."
            print("Nonexistent user login request from {}".format(username))
        else:    
            # check if duplicate active user
            if self.clients[username]["active"]:
                n.success = False
                n.error = "You are already logged in elsewhere."
                print("Duplicate user login request from {}.".format(username))
            else:
                # temporarily store user queue
                queued = self.clients[username]["queue"]
                self.clients[username]["queue"] = queue.SimpleQueue()
                # once user activated, then re-queue undelivered messages
                self.clients[username]["active"] = True
                self.clients[username]["queue"] = queued
                print("{} logged back in!".format(username))
                n.success = True
        return n

    def Logout(self, request: chat.LogoutRequest, context):
        n = chat.LogoutReply()
        username = request.username
        if username not in self.clients.keys():
            n.success = False
            n.error = "No existing user found."
            print("Nonexistent user logout request from {}".format(username))
        else:
            # send disconenct message through chatstream
            disconnect = chat.ConnectReply()
            disconnect.active = False
            self.clients[username]["queue"].put(disconnect)
            # after disconnect message goes through, then set inactive
            self.clients[username]["active"] = False
            n.success = True
            print("{} left the chat.".format(username))
        print("finishes logout")
        return n

    def List(self, request: chat.ListRequest, context):
        query = request.query
        n = chat.ListReply()
        for user in self.clients.keys():
            # allow query wildcard search
            if fnmatch.fnmatch(user, query+'*'):
                n.users.append(user)
        print("Accounts listed.")
        n.success = True
        return n

    def Delete(self, request: chat.DeleteRequest, context):
        username = request.username
        n = chat.DeleteReply()
        if username in self.clients.keys():
            time.sleep(3) # safeguard
            # thread-cutting and other functions handled in logout
            # here, we just remove the user from the clients dictionary
            self.clients.pop(username)
            print("{} deleted successfully.".format(username))
            n.success = True
        else:
            n.success = False
            n.error = "No user found."
        return n
    
    def ServStream(self, request: chat.ServConnectRequest,context): 
        port = request.port
        print("Connection made between {} and {}".format(self.port, port))
            # infinite loop starts for each client
        while True:
            if self.is_master: # if we are primary
                if self.conns[port]["queue"].qsize() > 0: #queue of things to send to secondary
                    n = self.conns[port]["queue"].get(block=False)
                    yield n 

    
    def __listen_for_messages(self, port):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        n = chat.ServConnectRequest()
        n.port = self.port
        print(self.conns)
        # continuously wait for new messages from the server!
        for servConnectReply in self.conns[port]["conn"].ServStream(n):  
            print(servConnectReply.message) # placeholder

    def is_master_query(self,conn):
        n = chat.IsMasterRequest()
        reply = conn.IsMasterQuery(n)
        return reply 
    
    def IsMasterQuery(self, request: chat.IsMasterRequest):
        n = chat.IsMasterReply()
        n.master = self.is_master
        return n

    
    def test_server_activity(self,channel): # test if a given server is active
        TIMEOUT_SEC = random.randint(1,3) # each server can timeout differently
        try: 
            grpc.channel_ready_future(channel).result(timeout=TIMEOUT_SEC) 
            return True 
        except grpc.FutureTimeoutError: 
            return False
    
    def connect(self):
        for i in ports: 
            if i != self.port:  # all other possible servers except self
                channel = grpc.insecure_channel(address + ':' + str(i))
                if self.test_server_activity(channel): # check if active
                    print("Port {} is active".format(i))
                    self.conns[i] = {}
                    self.conns[i]["conn"] = rpc.ChatServerStub(channel) # add connection
                    self.conns[i]["queue"] = queue.SimpleQueue() # instantiate queue to send messages to secondaries
                    threading.Thread(target=self.__listen_for_messages(i), daemon=True).start()
        time.sleep(2)
        master_found = False
        for port in self.conns:
            # n = chat.IsMasterRequest()
            reply = self.is_master_query(self.conns[port]["conn"])
            if reply.master:
                master_found = True
                self.master = port
                print("Master found at port ", str(port))
                break
        if not master_found:
            # if len(self.conns) > 0:
            #     print("initiate master finding procedure")
            self.is_master = True # for now just make self master
            print("No master found; I am the master")


if __name__ == '__main__':
    port = int(input("Input port number from one of [2056,3056,4056]: "))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    rpc.add_ChatServerServicer_to_server(ChatServer(port), server)  # register the server to gRPC
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)
