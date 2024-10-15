import socket
import threading
import random
import sys
import logging

# Set up logging: one handler for the file and one for the console
file_handler = logging.FileHandler("client.log.txt")
# Save all debug and higher-level logs to the file
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
# Only show INFO and higher-level logs on the console
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

# Set up the root logger
logging.basicConfig(
    # Overall level (this is needed to ensure debug logs are captured)
    level=logging.DEBUG,
    handlers=[file_handler, console_handler]
)

# Function to generate a random 4-digit client ID
def generate_client_id():
    return str(random.randint(1000, 9999))

# Function to handle receiving messages from the server
def receive_messages(client_socket, client_id, running):
    while running[0]:  # Check the shared running flag
        try:
            message = client_socket.recv(1024)

            # Handle empty messages (i.e., server might have closed the connection)
            if not message:
                logging.debug("\nConnection closed by the server.")
                running[0] = False  # Set running to False to signal exit
                break  # Exit the loop

            decoded_message = message.decode('utf-8')

            # Clear the input line, print the message, and re-display the input prompt
            sys.stdout.write('\r' + ' ' * 80)  # Clear the current line
            # Print the server message
            sys.stdout.write(f"\r{decoded_message}\n")
            sys.stdout.write(client_id + ': ')  # Re-display the input prompt
            sys.stdout.flush()  # Ensure the buffer is flushed so the prompt shows immediately

        except UnicodeDecodeError:
            # Handle specific decoding errors
            logging.info("Error decoding message from the server.")
        except Exception as e:
            logging.debug(f"Error receiving message from the server: {e}")
            running[0] = False  # Set running to False to signal exit
            break  # Exit the loop


def client_program(client_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))
    logging.info("[CONNECTED] Connected to the server.")

    # Generate and send client ID to the server
    client_socket.send(client_id.encode('utf-8'))
    logging.info(f"Assigned Client ID: {client_id}")

    running = [True]  # Shared flag for controlling the thread

    # Start a thread to continuously listen for messages from the server
    thread = threading.Thread(target=receive_messages, args=(
        client_socket, client_id, running))
    thread.start()

    # Allow the client to send messages
    while running[0]:  # Continue only if the server is running
        try:
            message = input(client_id + ': ')
            if message.lower() == 'exit':
                client_socket.send(message.encode('utf-8'))
                break  # Break the loop to go to cleanup
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            running[0] = False  # Set running to False to signal exit
            break  # Break the loop on error

    logging.info("Closing connection...")
    sys.exit(0)  # Ensure the program exits


if __name__ == '__main__':
    client_id = generate_client_id()
    client_program(client_id)
