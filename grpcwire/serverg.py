from concurrent import futures
import sqlite3
import grpc
import time
import queue
import fnmatch
import threading
import chat_pb2 as chat
import chat_pb2_grpc as rpc

lock = threading.Lock()
class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self):
        with lock:
            conn = sqlite3.connect('./chat.db', check_same_thread=False)
            conn.row_factory = lambda cursor, row: row[0]
            self.c = conn.cursor()
        self.queue = {}
        # self.c.execute("CREATE TABLE accounts (username TEXT, active TEXT)")
        # self.c.execute("CREATE TABLE messages (sender TEXT, recipient TEXT, message TEXT)")
        # id = c.execute("SELECT id FROM messages ORDER BY timestamp DESC LIMIT 1")


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
        # counter = 0 
        # last_id = 0
        # infinite loop starts for each client
        while True:
            # Check if recipient is active, if they have queued messages
            with lock:
                # active = self.c.execute("SELECT active FROM accounts WHERE username = ?", (recipient,))
                messages = self.c.execute("SELECT message FROM messages WHERE recipient = ?", (recipient,)).fetchall()
            # Check if recipient is active, if they have queued messages

            if len(messages) > 0:
                with lock: 
                    message = self.c.execute("SELECT message FROM messages WHERE recipient = ?", (recipient,)).fetchone()
                    sender = self.c.execute("SELECT * FROM messages WHERE recipient = ?", (recipient,)).fetchone()
                    rowid = self.c.execute("SELECT rowid, * FROM messages WHERE recipient = ?", (recipient,)).fetchone()
                    self.c.execute("DELETE FROM messages WHERE rowid = ?", (rowid,))
                print(message)
                print(rowid)
                forward = chat.ConnectReply()
                forward.active = True # not disconnecting
                forward.sender = sender
                forward.recipient = recipient
                forward.message = message
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
            forward = chat.ConnectReply()
            forward.active = True # not disconnecting
            forward.sender = sender
            forward.recipient = recipient
            forward.message = message 
            with lock: 
                self.c.execute("INSERT INTO messages VALUES (?,?,?)", (sender, recipient, message))
                active = self.c.execute("SELECT active FROM accounts WHERE username = (?)", (recipient,))
            # reply with overall sendMessage success + print debugging statements
            n.success = True
            active = str(active)
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
                self.c.execute("INSERT INTO accounts VALUES (?, ?)", (username, 1)) 
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
        if username not in usernames:
            n.success = False
            n.error = "No existing user found."
            print("Nonexistent user login request from {}".format(username))
        else:    
            # check if duplicate active user
            if active == "TRUE":
                n.success = False
                n.error = "You are already logged in elsewhere."
                print("Duplicate user login request from {}.".format(username))
            else:
                # temporarily store user queue
                with lock:
                    self.c.execute("UPDATE accounts SET active = 'TRUE' WHERE username = (?)", (username,))
                # queued = self.clients[username]["queue"]
                # self.clients[username]["queue"] = queue.SimpleQueue()
                # # once user activated, then re-queue undelivered messages
                # self.clients[username]["active"] = True
                # self.clients[username]["queue"] = queued
                print("{} logged back in!".format(username))
                n.success = True
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
            disconnect = chat.ConnectReply()
            disconnect.active = False
            # self.clients[username]["queue"].put(disconnect)
            # after disconnect message goes through, then set inactive
            # self.clients[username]["active"] = False
            with lock: 
                self.c.execute("UPDATE accounts SET active = 'FALSE' WHERE username = (?)", (username,))
            n.success = True
            print("{} left the chat.".format(username))
        print("finishes logout")
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

if __name__ == '__main__':
    port = 13543
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)  # register the server to gRPC
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)
