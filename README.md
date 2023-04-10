# CS262-replication Using GRPC
## GRPC Protocol Usage and Setup: 

Clone the repository on each local computer that will be using the network (all clients and the server). 

### For Server:
Run ``python3 -m server`` in the grpcwire directory. If successful, you'll see a ``Starting server. Listening...``. This will allow the server to start listening to new clients that join and their commands. As clients join and make requests, important updates will be printed to the server command line. 

### For Clients:
 Run ``python3 -m client`` in grpcwire directory. 

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
