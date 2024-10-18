import socket
import threading
import logging
import sys

host = ''
port = 12345

# Configure logging to write to 'server.log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Lock for managing turn order or shared resources
lock = threading.Lock()

clients = []
game_state = {
    "turn": 0,
    "clients": [],
}

client_id_counter = 0  # Counter to keep track of client IDs


def notify_client_turn(client_socket):
    try:
        client_socket.sendall(b"It's your turn!\n")
    except (BrokenPipeError, ConnectionResetError):
        logging.warning(
            "Failed to notify client of turn. Connection might be broken.")


def handle_client(client_socket, client_id):
    global client_id_counter  # Access the global client_id_counter
    logging.info(f"Handling client {client_id}.")

    try:
        # Notify the client of connection and instructions only once
        client_socket.sendall(
            b"Welcome! Type 'pass' to pass your turn or 'exit' to leave.\n")

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8').strip()
                if not message:
                    break  # Client has disconnected

                # Process client message
                with lock:
                    if game_state["turn"] == client_id:
                        if message.lower() == "pass":
                            logging.info(
                                f"Client {client_id} passed their turn.")
                            game_state["turn"] = (
                                game_state["turn"] + 1) % len(game_state["clients"])
                            client_socket.sendall(b"Turn passed.\n")
                            next_client_socket = clients[game_state["turn"]]
                            notify_client_turn(next_client_socket)

                        elif message.lower() == "exit":
                            logging.info(
                                f"Client {client_id} requested to exit.")
                            break  # Exit the loop to disconnect the client
                        else:
                            client_socket.sendall(b"")
                    else:
                        client_socket.sendall(b"Not your turn.\n")
            except (ConnectionResetError, ConnectionAbortedError):
                logging.warning(f"Client {client_id} disconnected abruptly.")
                break  # Client disconnected abruptly

    finally:
        logging.info(f"Client {client_id} disconnected.")
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
            if client_id in game_state["clients"]:
                game_state["clients"].remove(client_id)

            # Decrement the client_id_counter when a client disconnects
            client_id_counter -= 1

            # Update game state in case of disconnect
            if len(game_state["clients"]) > 0:
                game_state["turn"] = game_state["turn"] % len(
                    game_state["clients"])

        client_socket.close()


def start_server():
    global client_id_counter  # Access the global client_id_counter
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Limit to 2 clients

    logging.info("Server started, waiting for clients...")
    try:
        while True:
            client_socket, addr = server_socket.accept()

            logging.info(f"Client {client_id_counter} connected from {addr}.")

            with lock:
                clients.append(client_socket)
                game_state["clients"].append(client_id_counter)

            thread = threading.Thread(
                target=handle_client, args=(client_socket, client_id_counter))
            thread.start()

            # Notify if the client connected and is immediately the first to have their turn
            if len(game_state["clients"]) == 1:
                notify_client_turn(client_socket)

            client_id_counter += 1  # Increment the client ID counter for the next client

    except KeyboardInterrupt:
        logging.info("Server shutting down gracefully...")
        for client in clients:
            client.close()
        server_socket.close()
        sys.exit(0)


if __name__ == "__main__":
    start_server()
