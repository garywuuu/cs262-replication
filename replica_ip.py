from concurrent import futures
import sqlite3
import grpc
import time
import queue
import fnmatch
import random
import threading
import os
import shutil

import chat_pb2 as chat
import chat_pb2_grpc as rpc

# address = 'localhost'
# ports = [2056,3056,4056]
gary = "65.112.8.24"
jessica = "65.112.8.50"
ports = {
    2056: "65.112.8.50", #jessica
    3056: "65.112.8.24", #gary
    4056: "65.112.8.50"
}
lock = threading.Lock()

class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self,port):
        self.port = port
        filename = "./chat{}.db".format(port)
        with lock:
            conn = sqlite3.connect(filename, check_same_thread=False)
            conn.row_factory = lambda cursor, row: row[0]
        # times = []
        # for i in ports:
        #     path = "C:\desktop\cs262-replication\chat{}.db".format(i)
        #     times.append(os.path.getmtime(path))
        # if min(times) == os.path.getmtime("C:\desktop\cs262-replication\chat{}.db".format(self.port)):
        #     for i in ports:
        #         if i != self.port:
        #             src = "C:\Desktop\cs262-replication\grpcwire\chat{}.db".format(self.port)
        #     # dest contains the path of the destination file
        #             dest = "C:\Desktop\cs262-replication\grpcwire\chat{}.db".format(i)
        #             path = shutil.copyfile(src,dest)

        self.c = conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS accounts (username TEXT, active TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS messages (sender TEXT, recipient TEXT, message TEXT)")
        self.is_master = False
        self.master = None
        self.conns = {} # dict of all connections to other servers, key (port) -> value (connection)
        self.channels = {}

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
            with lock:
                messages = self.c.execute("SELECT message FROM messages WHERE recipient = ?", (recipient,)).fetchall()
            # Check if recipient is active, if they have queued messages

            if len(messages) > 0:
                print("Messages to send")
                with lock: 
                    message = self.c.execute("SELECT message FROM messages WHERE recipient = ?", (recipient,)).fetchone()
                    sender = self.c.execute("SELECT * FROM messages WHERE recipient = ?", (recipient,)).fetchone()
                    rowid = self.c.execute("SELECT rowid, * FROM messages WHERE recipient = ?", (recipient,)).fetchone()
                    self.c.execute("DELETE FROM messages WHERE rowid = ?", (rowid,))
                
                # Create structure of message to forward to other servers
                forward = chat.ConnectReply(); forward.active = True
                forward.message = message; forward.sender = sender # not disconnecting
                forward.sender = sender; forward.recipient = recipient

                print("Sending to recipient")
                
                yield forward


    def SendMessage(self, request: chat.MessageRequest, context):
        # parse out request
        sender = request.sender
        recipient = request.recipient
        message = request.message
        # create reply object
        n = chat.MessageReply()
        # check if user exists
        with lock:
            usernames = self.c.execute("SELECT username FROM accounts").fetchall()
        if recipient not in usernames:
            n.success = False
            n.error = "Recipient not found."
        else:
            # regardless of whether user is active, we'll push to queue
            with lock: 
                self.c.execute("INSERT INTO messages VALUES (?,?,?)", (sender, recipient, message))
                active = self.c.execute("SELECT active FROM accounts WHERE username = ?", (recipient,)).fetchone()
            # reply with overall sendMessage success + print debugging statements
            servMessage = chat.CommitRequest(); servMessage.port = self.port
            servMessage.active = True; servMessage.message = message
            servMessage.sender = sender; servMessage.receiver = recipient
            for port in self.conns: # add to each connection queue
                    # self.conns[port]["queue"].put(servMessage) 
                    reply = self.commit(port, servMessage)
                    if reply.success:
                        print("ACK received from port {} commit".format(port))
                    else:
                        print(reply.error)
            n.success = True
            if active == "TRUE":
                print("Sent: [{} -> {}] {}".format(sender,recipient,message))
            else: 
                print("Queued: [{} -> {}] {}".format(sender,recipient,message))
        return n
    

    def Signup(self, request: chat.SignupRequest, context):
        n = chat.SignupReply()
        username = request.username
        # if user already exists
        with lock: 
            usernames = self.c.execute("SELECT username FROM accounts").fetchall()
        if username in usernames:
            n.success = False
            n.error = "Username already exists."
            print("Signup from {} failed: User already exists.".format(username))
        else:
            # add new user dictionary to client dictionary
            # initiate empty thread-safe queue for msgs
            with lock:
                self.c.execute("INSERT INTO accounts VALUES (?,?)", (username, "TRUE"))
            
            servMessage = chat.CommitRequest(); servMessage.port = self.port
            servMessage.active = True; servMessage.message = f"INSERT INTO accounts VALUES ({username},TRUE)"# not disconnecting
            servMessage.sender = ""; servMessage.receiver = username
                
            for port in self.conns: # add to each connection queue
                    # self.conns[port]["queue"].put(servMessage) 
                reply = self.commit(port, servMessage)
                if reply.success:
                    print("ACK received from port {} commit".format(port))
                else:
                    print(reply.error)
            # self.clients[username] = {"active": True, "queue": queue.SimpleQueue()}
            print("New user {} has arrived!".format(username))
            n.success = True
        return n

    def Login(self, request: chat.LoginRequest, context):
        n = chat.LoginReply()
        username = request.username
        # check if user exists
        with lock:
            usernames = self.c.execute("SELECT username FROM accounts").fetchall()
            active = self.c.execute("SELECT active FROM accounts WHERE username = (?)", (username,))

        # if user doesn't exist
        if username not in usernames:
            n.success = False
            n.error = "No existing user found."
            print("Nonexistent user login request from {}".format(username))
        else:    
            # check if duplicate active user
            if active == "TRUE":
                n.success = False; n.error = "You are already logged in elsewhere."
                print("Duplicate user login request from {}.".format(username))
            else:
                # temporarily store user queue
                with lock:
                    self.c.execute("UPDATE accounts SET active = 'TRUE' WHERE username = (?)", (username,))
                print("{} logged back in!".format(username)); n.success = True
        return n

    def Logout(self, request: chat.LogoutRequest, context):
        n = chat.LogoutReply(); username = request.username
        with lock:
            usernames = self.c.execute("SELECT username FROM accounts").fetchall()
        if username not in usernames:
            n.success = False
            n.error = "No existing user found."
            print("Nonexistent user logout request from {}".format(username,))
        else:
            # send disconenct message through chatstream
            disconnect = chat.ConnectReply(); disconnect.active = False
            # after disconnect message goes through, then set inactive
            with lock: 
                self.c.execute("UPDATE accounts SET active = 'FALSE' WHERE username = (?)", (username,))
            n.success = True
            print("{} left the chat.".format(username))
        return n

    def List(self, request: chat.ListRequest, context):
        query = request.query; n = chat.ListReply()
        with lock:
            usernames = self.c.execute("SELECT username FROM accounts").fetchall()
        for user in usernames:
            # allow query wildcard search
            if fnmatch.fnmatch(user, query+'*'):
                n.users.append(user)
        print("Accounts listed.")
        n.success = True
        return n

    def Delete(self, request: chat.DeleteRequest, context):
        username = request.username; n = chat.DeleteReply()
        with lock:
            usernames = self.c.execute("SELECT username FROM accounts").fetchall()
        if username in usernames:
            time.sleep(3) # safeguard
            # thread-cutting and other functions handled in logout
            # here, we just remove the user from the clients dictionary
            self.clients.pop(username)
            with lock: 
                self.c.execute("DELETE FROM accounts WHERE username = (?)", (username,))
            print("{} deleted successfully.".format(username))
            n.success = True
        else:
            n.success = False
            n.error = "No user found."
        return n
 

    def is_master_query(self,port):
        n = chat.IsMasterRequest()
        reply = self.conns[port].IsMasterQuery(n)
        return reply 
    
    def IsMasterQuery(self, request: chat.IsMasterRequest, context):
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
        
    def add_connect(self, port):
        # "client" server tells "server" server to connect back
        n = chat.AddConnectRequest()
        n.requester_port = self.port
        n.replier_port = port 
        reply = self.conns[port].AddConnect(n)
        return reply
    
    def AddConnect(self, request: chat.AddConnectRequest, context):
        # "server" server receives request to connect back
        port = request.requester_port
        print("Receive connect request from {}".format(port))
        self.channels[port] = grpc.insecure_channel(address + ':' + str(port))
        self.conns[port] = rpc.ChatServerStub(self.channels[port])
        print("Connection successful")
        n = chat.AddConnectReply()
        n.success = True
        n.error = "Connection back to client-server failed"
        return n
    
    def commit(self, port, request: chat.CommitRequest):
        # primary server tells secondary server to write
        reply = self.conns[port].Commit(request)
        return reply
    
    def Commit(self, request: chat.CommitRequest, context): 
        # write to database here
        print("Received request to write to database")
        if request.sender != "":
            with lock:
                self.c.execute("INSERT INTO messages VALUES (?, ?, ?)", (request.sender, request.receiver, request.message))
                time.sleep(1)
                rowid = self.c.execute("SELECT rowid, * FROM messages WHERE recipient = ?", (request.receiver,)).fetchone()
                self.c.execute("DELETE FROM messages WHERE rowid = ?", (rowid,))
        else:
            with lock:
                self.c.execute("INSERT INTO accounts VALUES (?, ?)", (request.receiver, "TRUE"))
        n = chat.CommitReply()

        print(request.message)
        n.success = True 
        n.error = "Write to database failed"
        return n
    
    def connect(self):
        for i in list(ports.keys()): 
            if i != self.port:  # all other possible servers except self
                self.channels[i] = grpc.insecure_channel(ports[i] + ':' + str(i))
                if self.test_server_activity(self.channels[i]): # check if active
                    print("Port {} is active".format(i))
                    self.conns[i] = rpc.ChatServerStub(self.channels[i]) # add connection
                    self.add_connect(i)
                else: # delete inactive channel from dict
                    del self.channels[i]
        master_found = False
        for port in self.conns:
            reply = self.is_master_query(port)
            if reply.master:
                master_found = True
                self.master = port
                print("Master found at port {}".format(port))
                break
        if not master_found:
            self.is_master = True # for now just make self master
            print("No master found; I am the master")

    def disconnect(self, target_port):
        # "client" server tells "server" server to disconnect
        n = chat.DisconnectRequest()
        n.requester_port = self.port
        n.replier_port = target_port 
        n.is_master = self.is_master
        reply = self.conns[target_port].Disconnect(n)
        if reply.success:
            print("Port {} successfully disconnected".format(target_port))
            del self.conns[target_port] # remove from active conns
            self.channels[target_port].close() # close channel
            del self.channels[target_port]
        else:
            print(reply.error)
        return reply   

    def Disconnect(self, request: chat.DisconnectRequest, context):
        # "server" server receives request to disconnect
        port = request.requester_port
        print("Received discconnect request from {}".format(port))
        del self.conns[port] # remove from active conns
        self.channels[port].close() # close channel
        del self.channels[port]
        print("Disconnect successful")
        n = chat.DisconnectReply()
        n.success = True
        n.error = "Disconnect back to client-server failed"
        if request.is_master: # disconnected server was the master
            self.find_new_master()
        return n

    def disconnect_all(self):
        # server tells all connected servers to shut down conns and channels
        replies = []
        print("Connections:",list(self.conns.keys()))
        for port in list(self.conns.keys()):
            print("Disconnecting from {}".format(port))
            # self.disconnect(port)
            reply = self.disconnect(port)
            replies.append(reply)
        return replies

    def find_new_master(self):
        print("Finding new master")
        active_ports = list(self.conns.keys()) + [self.port]
        active_ports.sort()
        print("Active ports:", active_ports)
        new_master = active_ports[0]
        self.master = new_master
        if new_master == self.port:
            self.is_master = True
            print("I am now the master")
        else:
            print("Port {} is the new master".format(new_master))
        

if __name__ == '__main__':
    port = int(input("Input port number from one of [2056,3056,4056]: "))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    chat_server = ChatServer(port)    
    try: 
        rpc.add_ChatServerServicer_to_server(chat_server, server)  # register the server to gRPC
        print('Starting server. Listening...')
        server.add_insecure_port('[::]:' + str(port))
        server.start()
        while True:
            time.sleep(64 * 64 * 100)
    except:
        chat_server.disconnect_all()