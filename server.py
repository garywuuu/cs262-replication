import socket
import threading 
import fnmatch
import _thread

class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.start()

lock = _thread.allocate_lock()

# Track all users who have created accounts and map usernames to IP info
clients = {}

# List of active users by username -> ie john, jerry, jack
# Used to display active users and for detecting when users are online
active_users = []

# Dictionary mapping username to corresponding list of undelivered messages
undelivered_messages = {}

# For each user, create thread
def threaded(user):
	# At the start of the session, track username 
	# Helpful since our data structures use username as keys
	user.send(("What's your username?").encode('UTF-8'))
	username = (user.recv(1024)).decode('UTF-8')

	# Duplicate bool tracks whether multiple IP's are trying to use the same account/username
	duplicate = False 
	with lock: 
		if username in active_users:
			duplicate = True
			# While loop that insists on having only one IP access a given account at a time
			while duplicate == True:
				user.send((username + " is already logged in. Choose a different account: what's your username?").encode('UTF-8'))
				# Get new username and continue only if it's not currently being used
				username = (user.recv(1024)).decode('UTF-8')
				if username not in active_users:
					duplicate = False

	# Logic for when a user is logging back into an account they previously made
		if username in clients.keys():
			# Update the IP information so that new messages are sent to the right place
			clients[username] = user; active_users.append(username)
			print(username + " added to server!")
			# Nice Greeting
			user.send(("Welcome to Chat262, " + username +"!").encode('UTF-8'))
			# Since user is logging back in, we consider them active again

	# Feature 1: Creating an account with supplied username
		else:
			# Set IP info, initialized undelivered messages list for user, send a greeting, and add to active users. 
			clients[username] = user; undelivered_messages[username] = []
			print(username + " added to server!")
			user.send(("Welcome to Chat262, " + username +"!").encode('UTF-8'))
			active_users.append(username)

	# Deliver messages sent to user when they were offline. This is done only when first logging back in and not
	# during following while loop since they will receive messages normally while signed in and active
	deliver_undelivered(username)
	# While user is active, allow them to send/receive messages and call commands
	while True:
		try:
			data = (user.recv(1024)).decode('UTF-8')

			# Track for when user has disconnected from socket, meaning no longer active. Close connection
			if not data:
				with lock:
					active_users.remove(username); user.close()
					print(username + " Disconnected")
		
			# Split up message into proper commands
			# Commands are written by the user in the form of Operation|Recipient(optional)|Value
			data_list = data.split('|'); task = data_list[0]
			
			# Abstracting away logic for each command with this function
			with lock:
				check_operations(task, user, data_list, username)

		except:
		# Catch errors
			user.close(); return False
			

# Abstraction Function
def check_operations(task, user, data_list, username):
	# Feature 2: Listing Accounts on the Network
	# Requirements: user must command "list|all" or "list|active" to show all or just active users
	if task == "list":
		# Invalid Command
		if len(data_list) != 2:
			user.send(("Invalid Command - use list|all, list|active, or list|_").encode('UTF-8'))
			return False

		# Valid Command
		else:
			action = data_list[1]
			list_accounts(user, action); print("listed")

	# Feature 3: Active user can send a message to recipient
	# Requirements: user must follow the structure "send|recipient|message"
	elif task == "send":
		# Check valid command structure
		if len(data_list) != 3:
			user.send(("Invalid command - send|recipient|message").encode('UTF-8'))
			return False

		# User must specify message receiver
		receiver_username = data_list[1]

		# Logic if receiver has an account
		if receiver_username in clients.keys():
			# Build message
			message = ("| From " + username + ": "+ data_list[2]).encode('UTF-8')
			# Send immediately if recipient is active
			if receiver_username in active_users:
				sendmessage(message, username, receiver_username)

			# Queue message in undelivered_messages if recipient offline
			else:
				undelivered_messages[receiver_username].append(message)
				sendmessage(("Message queued when user returns").encode("UTF-8"), username, receiver_username)
				print("Message queued")

		# Recipient does not exist
		else:
			user.send(("Recipient is not a user in the network").encode('UTF-8'))

	# Feature 4: removing user from network
	# Specifications: user can only remove themselves from the network. As such, we don't need to worry about
	# receiving undelivered messages since they received them upon signing in already. 
	elif task == "remove":
		remove_user(username, user); print("Removed " + username + " from network.")

# Logic for delivering undelivered messages to user who signed back in
def deliver_undelivered(username):
	# Loop through messages and send. Clear list when done. 
	for msg in undelivered_messages[username]:
		clients[username].send(msg)
	undelivered_messages[username].clear()

# Logic for sending a message
def sendmessage(message, username, receiver_username):
	# Try sending message to recipient
	try:
		clients[receiver_username].send(message)
		clients[username].send(("Message sent successfully!").encode("UTF-8"))
		print(username + " sent a message to " + receiver_username)
	except:
		clients[receiver_username].close()


# Logic for listing all or just active accounts
def list_accounts(recipient, s):	
	if s == "active":
		users = "Users: | "+''.join(str(n)+" | " for n in active_users)
		recipient.send(users.encode('UTF-8'))
	elif s == "all":
		users = "Users: | "+''.join(str(n)+" | " for n in clients.keys())
		recipient.send(users.encode('UTF-8'))
	else:
		users = "Users: | "+''.join(str(n)+" | " for n in clients.keys() if fnmatch.fnmatch(n, s+'*'))
		recipient.send(users.encode('UTF-8'))

# Logic for removing user from network
def remove_user(username, user):
	# Since users can only remove themselves from network, they will have already seen previously undelivered messages
	# after logging in before removing their account. 
	del clients[username]
	active_users.remove(username)
	user.close()
	return False

# Main function
def main():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	IP = "127.0.0.1"
	port=5000
	server.bind((IP, port))
	server.listen(100)
	print("Listening on port " + str(port))
	
	while True:
		# Each new user connecting to server
		user, addr = server.accept() 
		print (addr[0] + " connected")	
		print('Connected to :', addr[0], ':', addr[1])
		# Start new thread
		_thread.start_new_thread(threaded, (user,))
	server.close()

if __name__=='__main__':
	main()