import socket
import threading
import logging
import sys

# Global variables
host = '127.0.0.1'  # Localhost (for now)
port = 12345        # Arbitrary port number
clients = []        # List to keep track of connected clients
server_socket = None  # Global server socket variable

# Function to handle individual client connections
def handle_client(client_socket, address):
    print.info(f"[NEW CONNECTION] {address} connected.")
    clients.append(client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Echo message back to the client
                client_socket.send("Message received!".encode('utf-8'))
            else:
                raise ConnectionError("Client disconnected.")
        except Exception as e:
            break

    # Remove client after disconnection
    clients.remove(client_socket)
    client_socket.close()

# Function to start the server and listen for incoming connections
def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            # Create a new thread to handle the client connection
            thread = threading.Thread(
                target=handle_client, args=(client_socket, client_address))
            thread.start()
    except KeyboardInterrupt:
        for client in clients:
            client.close()
        server_socket.close()
        sys.exit(0)


if __name__ == "__main__":
    start_server()
