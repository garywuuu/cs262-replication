# CS262-replication Using GRPC
## GRPC Protocol Usage and Setup: 

Clone the repository on each local computer that will be using the network (all clients and the server). 

### For Server:
Run ``python3 -m replica`` in the replica directory. Each server process will input a different port. Leader election is done such that the lowest port number is chosen if there is no current leader. If successful, you'll see a ``Starting server. Listening...``. Connect the other two clients in separate processes with different port numbers, and they will create connections between each other. This will allow the server to start listening to new clients that join and their commands. As clients join and make requests, important updates will be printed to the server command line. 

### For Clients:
 Run ``python3 -m clientg`` in base directory. 

### Fault Tolerance:
This implementation implements Fault Tolerance through the use of the Master/Secondary replication model, where all client interaction is done with the master server, and the master forwards that request to the secondary replicas. Upon the secondaries acknowledging that they have written the request to their sqlite databases, the master then carries out the request. The servers each know who the master is at any given time, so if the master goes down, the lowest port secondary will take over as master and the clients will automatically connect to the new master. Since the secondaries have the most updated state in their databases, no messages are lost. 

### Persistence: 
The sqlite3 database is written to at every step for each replica, so in the case that all servers go down, we still have the most updated state of what was done before all the servers went down. 

### Command Documentation:
#### Signup and Login:
Upon starting up the client, you'll be given the options to either sign up or log in. The prompt will specify the available commands ``Enter 1|{Username} to sign up or 2|{Username} to log in:``. 

There are mechanisms in place to ensure successful login: you must enter a valid input, you can't sign up with an existing username, you can't log in to a nonexistent user, and you can't log in to a user already logged in elsewhere.

Once successfully logged in, you'll be given the following command options: ``Commands: \send to send a message, \logout to log out, \list to list accounts.``
<br/><br/>

#### Sending Messages:
To send a message, input the ``\send`` command. Then, you'll be prompted to specify a ``recipient`` and a ``message``. Both must be non-empty.

If the recipient is active on the network, the message will be sent immediately. If the recipient is inactive, the message will accumulate in a queue to be sent once they log back in.
   
If the recipient username does not exist in the network, you will be prompted with sending a new command. 
<br/><br/>

#### Listing Accounts: 
To list accounts, input the ``\list`` command. You will then be prompted to give a query. This query may either be empty or a string. The terminal will then print out all usernames that begin with the query.
<br/><br/>

#### Logging Out: 
To log out, input the ``\logout`` command or ``Ctrl+C`` for a keyboard interrupt. Once logged out, the server will show that the user has the chat and the client will return to the original signup and login prompt.
<br/><br/>

#### Removing Account: 
To log out, input the ``\delete`` command. The terminal will then prompt you for confirmation. If you confirm with ``y``, then your account will be deleted and the client will return to the original signup and login prompt.

## Engineering Notebook
Nothing fancy, just a Google Doc: https://docs.google.com/document/d/1JumuPWBkNpIlMaTkpVAO0D-whaUzeqRK3y-t_MS-yHM/edit?usp=sharing
