import socket
import threading
import sys
import logging
from threading import Lock

clients_lock = Lock()
client_ids_lock = Lock()
client_game_state_lock = Lock()

# Global variables
host = ''
port = 12345
clients = []  # List to keep track of connected clients
client_ids = {}  # Dictionary to map client sockets to their IDs
guess_word = ['a', 'b', 'c', 'd']  # Target word

# Dictionary to store each client's game state (guessed word, target word)
client_game_state = {}

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log.txt"),
        logging.StreamHandler()
    ]
)


def guess_letter(guess, player_word):
    updated_word = list(player_word)
    for i, letter in enumerate(guess_word):
        if guess == letter:
            updated_word[i] = letter

    # Return the updated word as a string
    return ''.join(updated_word)

# Function to broadcast a message to all client
def broadcast(message, client_socket):
    for client in clients:
        # Don't send the message to the sender
        if client != client_socket:
            try:
                client.send(message)
            except socket.error as e:
                logging.error(f"Socket error occurred: {e}")
                client.close()
                clients.remove(client)

# Function to send a message to a specific client
def send_to_client(client_socket, message):
    try:
        client_socket.send(message.encode('utf-8'))
    except socket.error as e:
        logging.error(f"Error sending message to client: {e}")
        client_socket.close()
        if client_socket in clients:
            clients.remove(client_socket)

# Function to handle individual client connections
def handle_client(client_socket, address):
    global guess_word
    player1_word = ['_', '_', '_', '_']
    logging.info(f"[NEW CONNECTION] {address} connected.")

    # Safely add client
    with clients_lock:
        clients.append(client_socket)

    # Receive the client's ID when they first connect
    client_id = client_socket.recv(1024).decode('utf-8')
   
    # Safely store client ID
    with client_ids_lock:
        client_ids[client_socket] = client_id

    logging.info(f"[{address}] Assigned Client ID: {client_id}")

    # Initialize the player's word to be empty (underscore for unguessed letters)
    player_word = ['_'] * len(guess_word)  # A blank word initially
    
    # Safely save this player's word state
    with client_game_state_lock:
        client_game_state[client_socket] = player_word

    while True:
        try:
            message = client_socket.recv(1024)
            if message:

                if message.decode('utf-8') == 'exit':
                    logging.info(f"Client {client_id} has requested to exit.")

                    # Notify other clients
                    broadcast(f"Player {client_id} has disconnected.".encode(
                        'utf-8'), client_socket)
                    logging.info(f"Client {client_id} has disconnected.")
                    break  # Exit the loop to end the connection

                if message.decode('utf-8')[:5] == "check":

                    # Send the current state of the player's guessed word
                    player_word = client_game_state[client_socket]
                    send_to_client(
                        client_socket, f"Current Word: {''.join(player_word)}")
                    logging.info(
                        f"Client {client_id} checked their word: {''.join(player_word)}")

                elif message.decode('utf-8')[:5] == "guess":

                    guessed_letter = message.decode('utf-8')[6:7]
                    player_word = client_game_state[client_socket]
                    updated_word = guess_letter(guessed_letter, player_word)
                    client_game_state[client_socket] = list(updated_word)

                    # Send the updated word back to the guessing client
                    send_to_client(
                        client_socket, f"Updated Word: {updated_word}")

                    # Optionally log the updated word
                    logging.info(
                        f"[{client_id}] Guessed {guessed_letter}, Updated word: {updated_word}")

                else:
                    # Prefix the message with the client's ID before broadcasting
                    broadcast(f"{client_id}: {message.decode('utf-8')}".encode('utf-8'), client_socket)
                    logging.info(f"[{client_id}] {message.decode('utf-8')}")
                    # print("message: ", message.decode('utf-8')[:5])
             
        except Exception as e:
            logging.debug(f"[ERROR] {address} disconnected: {e}")
            break

    # Clean up client state on disconnection
    with clients_lock:
        clients.remove(client_socket)

    with client_ids_lock:
        del client_ids[client_socket]

    with client_game_state_lock:
        if client_socket in client_game_state:
            del client_game_state[client_socket]

    client_socket.close()

# Function to start the server and listen for incoming connections
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    logging.info(f"[LISTENING] Server is listening on {host}:{port}")
    try:
        while True:
            client_socket, client_address = server.accept()

            # Create a new thread to handle the client connection
            thread = threading.Thread(
                target=handle_client, args=(client_socket, client_address))
            thread.start()
            logging.info(
                f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        logging.debug("[SHUTTING DOWN] Server is shutting down...")
    finally:
        # Cleanup: close all client sockets
        for client in clients:
            client.close()
        server.close()
        logging.info(
            "[CLEANUP] Closed all client connections and server socket.")


if __name__ == "__main__":
    logging.info("[STARTING] Server is starting...")
    start_server()
