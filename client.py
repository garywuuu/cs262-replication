import threading
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

# Receiving messages from server
def receive():
    while True:
        try:
            message = client.recv(1024).decode('UTF-8'); print(message)
        except:
            print('Error receiving message from server'); client.close()
            break

# Sending messages to server
def send():
    while True:
        ans = input('\n')
        client.send(ans.encode('UTF-8'))
        

def main():
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    send_thread = threading.Thread(target=send)
    send_thread.start()

if __name__=='__main__':
	main()