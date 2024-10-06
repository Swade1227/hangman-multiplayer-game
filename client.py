import socket
import threading
import sys

# Function to send messages to the server
def send_messages(client_socket):
    while True:
        message = input("You: ")
        if message.lower() == "exit":  # Client requests disconnection
            client_socket.send(message.encode('utf-8'))  # Notify the server
            print("[DISCONNECTED] You have disconnected from the server.")
            client_socket.close()
            break  # Exit the send thread
        else:
            client_socket.send(message.encode('utf-8'))

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                raise ConnectionError("Connection closed by the server.")
            # Clear current input line and move to the start of the line
            sys.stdout.write("\r")  # Move to the start of the line
            sys.stdout.flush()      # Flush to clear the buffer
            # Print server's message without interfering with user input
            # Print server message and move to next line
            print(f"\rServer: {message}\n", end='')
            # Redisplay the input prompt for the user to continue typing
            sys.stdout.write("You: ")
            sys.stdout.flush()
        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.close()
            break

def start_client():
    host = '127.0.0.1'
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((host, port))
        print("[CONNECTED] Connected to the server.")

        # Start a thread to handle sending messages
        send_thread = threading.Thread(
            target=send_messages, args=(client_socket,))
        send_thread.start()

        # Start a thread to handle receiving messages
        receive_thread = threading.Thread(
            target=receive_messages, args=(client_socket,))
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

    except Exception as e:
        print(f"[ERROR] Could not connect to the server: {e}")


if __name__ == "__main__":
    start_client()
