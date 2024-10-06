import socket
import threading
import random
import sys

# Function to generate a random 4-digit client ID
def generate_client_id():
    return str(random.randint(1000, 9999))

# Function to handle receiving messages from the server
def receive_messages(client_socket, client_id):
    while True:
        try:
            message = client_socket.recv(1024)

            # Handle empty messages (i.e., server might have closed the connection)
            if not message:
                print("Connection closed by the server.")
                client_socket.close()
                break

            decoded_message = message.decode('utf-8')

            # Clear the input line, print the message, and re-display the input prompt
            sys.stdout.write('\r' + ' ' * 80)  # Clear the current line
            # Print the server message
            sys.stdout.write(f"\r{decoded_message}\n")
            sys.stdout.write(client_id + ': ')  # Re-display the input prompt
            sys.stdout.flush()  # Ensure the buffer is flushed so the prompt shows immediately

        except UnicodeDecodeError:
            # Handle specific decoding errors
            print("Error decoding message from the server.")
        except Exception as e:
            print(f"Error receiving message from the server: {e}")
            client_socket.close()
            break


def client_program(client_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))
    print("[CONNECTED] Connected to the server.")

    # Generate and send client ID to the server
    client_socket.send(client_id.encode('utf-8'))
    print(f"Assigned Client ID: {client_id}")

    # Start a thread to continuously listen for messages from the server
    thread = threading.Thread(target=receive_messages, args=(client_socket,client_id))
    thread.start()

    # Allow the client to send messages
    while True:
        try:
            message = input(client_id + ': ')
            if message.lower() == 'exit':
                client_socket.send(message.encode('utf-8'))
                client_socket.close()
                break
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            client_socket.close()
            break


if __name__ == '__main__':
    client_id = generate_client_id()
    client_program(client_id)
