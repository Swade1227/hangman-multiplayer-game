import socket
import threading
import logging
import sys
import argparse

host = ''
port = 12345

# =========== LOGGING ===========

# clears the server log file
open("client.log.txt", "w").close()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("client.log.txt"),
    ]
)


# =========== RECIEVE FROM SERVER ===========

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message:
                print(message)
                logging.info(f"Received from server: {message.strip()}")
            else:
                print("Disconnected from server.")
                logging.info("Disconnected from server.")
                break
        except Exception as e:
            print("Disconnected from server.")
            logging.error(f"Error receiving message: {e}")
            break


def main(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        logging.info(f"Connected to server at {host}:{port}")

        threading.Thread(target=receive_messages, args=(client_socket,)).start()

        while True:
            message = input()
            if message == "exit":
                client_socket.send(message.encode('utf-8'))
                logging.info("Sent exit command to server.")
                break
            elif message == "guess":
                client_socket.send(message.encode('utf-8'))
                logging.info("Sent pass command to server.")
            else:
                client_socket.send(message.encode('utf-8'))
                logging.info(f"Sent message to server: {message.strip()}")
                continue

    except ConnectionRefusedError:
        print("Unable to connect to the server.")
        logging.error("Unable to connect to the server.")
    finally:
        client_socket.close()
        logging.info("Client socket closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect to the server.")
    parser.add_argument('--host', required=True, help="Server IP address or hostname to connect to")
    parser.add_argument('--port', type=int, required=True, help="Port on which the server is listening")
    args = parser.parse_args()

    main(args.host, args.port)
