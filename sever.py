import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

clients = {}  # Dictionary to store connected clients

def handle_client(client_socket, client_address):
    try:
        # Receive the username from the client
        username = client_socket.recv(1024).decode()
        print(f"User {username} connected from {client_address}")
        clients[username] = client_socket

        while True:
            message = client_socket.recv(2048).decode('utf-8')
            if message:
                broadcast_message(username, message)
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        if username in clients:
            del clients[username]
            client_socket.close()

def broadcast_message(sender_username, message):
    for username, client_socket in clients.items():
        if username != sender_username:
            try:
                client_socket.sendall(f"{sender_username}~{message}".encode())
            except Exception as e:
                print(f"Error broadcasting message to {username}: {e}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()
