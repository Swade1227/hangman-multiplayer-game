import socket
import threading
import logging
import sys
import argparse
import random

host = ''
port = 12345

# =========== LOGGING ===========

# clear the server log
open("server.log.txt", "w").close()

# configure logging to write to 'server.log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)


# =============== GLOBAL VARIABLES FOR GAME STATE ===============

# lock for managing turn order or shared resources
lock = threading.Lock()
clients = []
client_words = {}  # Store each client's unique word
game_state = {
    "turn": 0,
    "clients": [],
}


WORD_LIST = ["python", "server", "socket", "client","database", "algorithm", "function", "API", "port","connection", "protocol", "packet", "encryption", "security","request", "response", "debug", "thread", "multithreading","scripting", "web", "interface", "cloud", "storage", "load","json", "xml", "framework", "frontend", "backend", "performance"]
global_word = "net"

# counter to keep track of client IDs
client_id_counter = 0


def broadcast_message(message):
    """sends a message to all connected clients."""
    for client in clients:
        try:
            client.sendall(message.encode('utf-8'))
        except:
            logging.warning("Failed to send message to a client.")


def create_blank_word():
    return ['_' for _ in global_word]


def update_client_word(client_id, guessed_letter):
    client_word = client_words.get(client_id)
    if client_word:
        for idx, letter in enumerate(global_word):
            if letter == guessed_letter:
                client_word[idx] = guessed_letter
        return client_word
    return None


def notify_client_turn(client_socket):
    try:
        client_socket.sendall(b"It's your turn!\n")

        if len(clients) > 1:
            # Get the other value
            if clients[0] == client_socket:
                other_client_socket = clients[1]
            else:
                other_client_socket = clients[0]

            other_client_socket.sendall(b"Waiting on Opponent...\n")
        
    except (BrokenPipeError, ConnectionResetError):
        logging.warning("Failed to notify client of turn. Connection might be broken.")


def reset_game():

    logging.info("Resetting Game State")

    """Resets the game state for a new round."""
    global global_word, client_words

    global_word = random.choice(WORD_LIST)
    logging.info(f"The new word is: {global_word} (hidden from clients)")

    logging.info("")

    # Reset each client's progress
    for client_id in game_state["clients"]:
        client_words[client_id] = create_blank_word()

    # Reset the turn to the first player
    game_state["turn"] = 0

    # Notify all clients of the reset
    broadcast_message("The game has been reset! A new word has been chosen.\nWelcome! Type a letter to guess or 'exit' to leave.\n")

    # Notify the first client of their turn
    first_client_socket = clients[game_state["turn"]]
   


# =============== CLIENT HANDLING ===============

def handle_client(client_socket, client_id):

    # access lient_id_counter
    global client_id_counter
    logging.info(f"Handling client {client_id}.")

    try:

        # welcome message
        client_socket.sendall(b"Welcome! Type a letter to guess or 'exit' to leave.\n")
        if len(clients) > 1:
            # Get the other value
            if clients[0] == client_socket:
                other_client_socket = clients[1]
            else:
                other_client_socket = clients[0]

            # other_client_socket.sendall(b"Its your turn.\n")
            client_socket.sendall(b"Not your turn, waiting on opponent...\n")

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8').strip()

                # client disconnected
                if not message:
                    break

                # process client message
                with lock:
                    if game_state["turn"] == client_id:

                        # client guessed a letter
                        if len(message) == 1 and message.isalpha():
                            guessed_letter = message.lower()
                            if guessed_letter in global_word:
                                client_word = update_client_word(client_id, guessed_letter)
                                logging.info(f"Client {client_id} guessed correctly: {guessed_letter}")
                                client_socket.sendall(f"\nCorrect! Your word: {''.join(client_word)}\n".encode('utf-8'))

                                if '_' not in client_word:
                                    broadcast_message(f"Client {client_id} has won... Word was: {global_word}\n")
                                    reset_game()

                            else:
                                logging.info(f"Client {client_id} guessed incorrectly: {guessed_letter}")
                                client_socket.sendall(b"\nIncorrect guess.\n")

                            # move to next turn
                            game_state["turn"] = (game_state["turn"] + 1) % len(game_state["clients"])
                            next_client_socket = clients[game_state["turn"]]

                            # notify next client its their turn
                            notify_client_turn(next_client_socket)

                        elif message.lower() == "exit":

                            logging.info(f"Client {client_id} requested to exit.")
                            break  # exit the loop to disconnect the client
                        else:
                            client_socket.sendall(b"Invalid input. Guess a letter or 'exit'.\n")
                    else:
                        client_socket.sendall(b"Not your turn.\n")
            except (ConnectionResetError, ConnectionAbortedError):
                logging.warning(f"Client {client_id} disconnected abruptly.")
                break  # client disconnected abruptly

    finally:
        # handle disconnection
        logging.info(f"Client {client_id} disconnected.")
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)

                # notify the remaining client
                if game_state["clients"]:
                    remaining_client_id = 0
                    if len(clients) > 0:
                        remaining_client_socket = clients[remaining_client_id]
                        remaining_client_socket.sendall(b"A player has disconnected. The game is resetting.\nIt is now your turn... Type a letter to guess or 'exit' to leave.\n")
                        game_state["turn"] = remaining_client_socket

            if client_id in game_state["clients"]:
                game_state["clients"].remove(client_id)
                del client_words[client_id]

            # reset unique words for a new game
            client_words.clear()
            for client in game_state["clients"]:
                # reset each player's word
                client_words[client] = create_blank_word()

        # update turn management
        client_id_counter -= 1
        game_state["turn"] = client_id_counter
        client_socket.close()


def start_server(host, port):
    global client_id_counter
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(2)
    logging.info(f"Server started on 0.0.0.0:{port}, waiting for clients...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"Client {client_id_counter} connected from {addr}.")
            with lock:
                clients.append(client_socket)
                game_state["clients"].append(client_id_counter)
                client_words[client_id_counter] = create_blank_word()

            thread = threading.Thread(target=handle_client, args=(client_socket, client_id_counter))
            thread.start()

            if len(game_state["clients"]) == 1:
                notify_client_turn(client_socket)

            client_id_counter += 1

    except KeyboardInterrupt:
        logging.info("Server shutting down...")
        for client in clients:
            client.close()
        server_socket.close()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-p', '--port', type=int,required=True, help="Port to bind the server to")
    args = parser.parse_args()

    start_server('0.0.0.0', args.port)
