import socket
import threading
import sys
import logging

# Global variables
host = '127.0.0.1'
port = 12345
clients = []  # List to keep track of connected clients
client_ids = {}  # Dictionary to map client sockets to their IDs

# Function to broadcast a message to all client
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:  # Don't send the message to the sender
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),  # Log to file
        logging.StreamHandler()  # Log to terminal
    ]
)

# Function to handle individual client connections
def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    clients.append(client_socket)

    # Receive the client's ID when they first connect
    client_id = client_socket.recv(1024).decode('utf-8')
    client_ids[client_socket] = client_id
    print(f"[{address}] Assigned Client ID: {client_id}")

    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                # Prefix the message with the client's ID before broadcasting
                broadcast(f"{client_id}: {message.decode('utf-8')}".encode('utf-8'), client_socket)
                print(f"[{client_id}] {message.decode('utf-8')}")
            else:
                raise ConnectionError("Client disconnected.")
        except Exception as e:
            print(f"[ERROR] {address} disconnected: {e}")
            break

    clients.remove(client_socket)
    del client_ids[client_socket]
    client_socket.close()

# Function to start the server and listen for incoming connections
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[LISTENING] Server is listening on {host}:{port}")

    while True:
        client_socket, client_address = server.accept()
        # Create a new thread to handle the client connection
        thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start_server()
