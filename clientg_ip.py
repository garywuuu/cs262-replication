
import threading
import grpc
import random
import time

import chat_pb2 as chat
import chat_pb2_grpc as rpc

# address = 'localhost'
# port = 11912
# servers = [2056,3056,4056]
gary = "65.112.8.24"
jessica = "65.112.8.50"
servers = {
    2056: "65.112.8.50", #jessica
    3056: "65.112.8.24", #gary
    4056: "65.112.8.50"
}

class Client:

    def __init__(self):
        # create a gRPC channel + stub
        self.username = None
        self.master = None
        self.channel = None
        self.conn = None

        # connect to each port to find master server 
        for port in list(servers.keys()):
            self.channel = grpc.insecure_channel(servers[port] + ':' + str(port))
            if self.test_server_activity(self.channel):
                print("Server at port {} is active".format(port))
                self.conn = rpc.ChatServerStub(self.channel) # add connection
                reply = self.is_master_query(port)
                if reply.master: # connection is master
                    self.master = port
                    print("Master found at port {}".format(port))
                    break
                else: 
                    self.conn = None # break connection
                    self.channel = None
        if self.conn is None:
            print("Error: no connection found.")
        if self.master is None: # no master found
            print("Error: no master found.")
                    
        # self.conn = rpc.ChatServerStub(channel)

    # thread creation separate from instantiation. called when username set.
    def thread(self):
        if self.username is not None:
            # create new listening thread for when new message streams come in
            threading.Thread(target=self.__listen_for_messages, daemon=True).start()
            print("Thread started: listening for messages from", str(self.master))

    def __listen_for_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        try: 
            if self.username is not None:
                # request message provides username
                n = chat.ConnectRequest()
                n.recipient = self.username
                # continuously  wait for new messages from the server!
                for connectReply in self.conn.ChatStream(n):  
                    # active boolean checks to see if this is a disconnect request
                    if connectReply.active:
                        # if normal active user message, we display it in chat
                        print("R[{}] {}".format(connectReply.sender, connectReply.message)) 
                    else: # if disconnect request, then need to return to terminate thread
                        return
        except:
            time.sleep(1) # servers need time to figure out who is master
            self.reconnect_server()

    def send_message(self, message, recipient):
        """
        This method is called when user enters something into the textbox
        """
        if recipient != '' and message != '':
            # construct message request
            n = chat.MessageRequest() 
            n.sender = self.username  
            n.recipient = recipient 
            n.message = message
            # print("S[{} -> {}] {}".format(n.sender, n.recipient, n.message)) 
            reply = self.conn.SendMessage(n)  # send to the server
            return reply
        else:
            print("Please enter a recipient and a message.")

    def signup(self, username):
        if username != '':
            n = chat.SignupRequest() 
            n.username = username
            reply = self.conn.Signup(n)
            if reply.success:
                self.username = n.username
            self.thread()
            return reply

    def login(self, username):
        if username != '':
            n = chat.LoginRequest() 
            n.username = username
            reply = self.conn.Login(n)
            if reply.success:
                self.username = n.username
            self.thread()
            return reply

    def logout(self):
        try: 
            n = chat.LogoutRequest()
            n.username = self.username
            reply = self.conn.Logout(n)
            if reply.success:
                self.username = None
                # print("Logout successful!")
            return reply
        except:
            time.sleep(1) # servers need time to figure out who is master
            self.reconnect_server()

    def list(self, query):
        n = chat.ListRequest()
        n.query = query
        reply = self.conn.List(n)
        return reply
        # if reply.success:
        #     for user in reply.users:
        #         print(user)
        # else:
        #     print("{}".format(reply.error))

    def delete(self):
        n = chat.DeleteRequest()
        n.username = self.username
        temp = self.logout()
        reply = self.conn.Delete(n)
        return reply
        # if reply.success:
        #     print("Account deleted.")
        # else:
        #     print("{}".format(reply.error))

    def test_server_activity(self,channel): # test if a given server is active
        TIMEOUT_SEC = random.randint(1,3) # each server can timeout differently
        try: 
            grpc.channel_ready_future(channel).result(timeout=TIMEOUT_SEC) 
            return True 
        except grpc.FutureTimeoutError: 
            return False
        
    def is_master_query(self,port):
        n = chat.IsMasterRequest()
        reply = self.conn.IsMasterQuery(n)
        return reply 
    
    def reconnect_server(self):
        # given disconnected server, connect to another master
        print("Reconnecting server")
        failed_port = self.master
        self.channel = None 
        self.master = None 
        self.conn = None

        for port in list(servers.keys()):
            if port != failed_port: # not the one that just disconnected
                self.channel = grpc.insecure_channel(servers[port] + ':' + str(port))
                if self.test_server_activity(self.channel):
                    print("Server at port {} is active".format(port))
                    self.conn = rpc.ChatServerStub(self.channel) # add connection
                    reply = self.is_master_query(port)
                    if reply.master: # connection is master
                        self.master = port
                        self.thread() # starts listening
                        print("Master found at port {}".format(port))
                        break
                    else: 
                        self.conn = None # break connection
                        self.channel = None
        if self.conn is None:
            print("Error: no connection found.")
        if self.master is None: # no master found
            print("Error: no master found.")


if __name__ == '__main__':
    c = Client()
    try:
        while True:
            try:         
                while c.username is None:
                    req = input("Enter 1|{Username} to sign up or 2|{Username} to log in: ")
                    if req[0:2] == "1|":
                        reply = c.signup(req[2:])
                        if reply.success:
                            print("Signup successful!")
                        else:
                            print("{}".format(reply.error))
                    elif req[0:2] == "2|":
                        reply = c.login(req[2:])
                        if reply.success:
                            print("Login successful!")
                        else:
                            print("{}".format(reply.error))
                    else:
                        print("Invalid input.")
                    # username set, can now start thread and take commands
                    if c.username is not None:
                        print("Commands: \send, \logout, \list, \delete.")
                    while c.username is not None:
                        request = input('')
                        if request == "\logout":
                            reply = c.logout()
                            if reply.success:
                                print("Logout successful!")
                        elif request == "\list":
                            query = input("Query: ")
                            reply = c.list(query)
                            if reply.success:
                                for user in reply.users:
                                    print(user)
                            else:
                                print("{}".format(reply.error))
                        elif request == "\send":
                            recipient = input("Recipient: ")
                            message = input("Message: ")
                            reply = c.send_message(message, recipient)
                            if reply is not None:
                                if reply.success:
                                    print("S[{}] {}".format(recipient, message)) 
                                else:
                                    print("{}".format(reply.error))
                        elif request == "\delete":
                            confirm = input("Are you sure you want to delete your account? [y]: ")
                            if confirm == "y":
                                reply = c.delete()
                                if reply.success:
                                    print("Account deleted.")
                                else:
                                    print("{}".format(reply.error))
                            else:
                                print("Account deletion cancelled.")
                        else:
                            print("Please enter a valid command.")
            except:
                c.channel.close() # important
                time.sleep(1) # servers need time to figure out who is master
                c.reconnect_server()
    except KeyboardInterrupt: # catch the ctrl+c keyboard interrupt
        if c.username is not None:
            temp = c.logout()