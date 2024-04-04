import socket
import threading

# Server configuration
HOST = 'localhost'
PORT = 8080

# client sockets and user info
clients = {}

# Active channels with lists of client sockets
channels = {"general": [], "testing": [], "channel 3": []}

def broadcast_to_channel(channel, message):
    for client in channels[channel]:
        try:
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Broadcast failed: {e}")

def remove_client(client_socket):
    info = clients.pop(client_socket, {})
    if info and info["channel"]:
        channels[info["channel"]].remove(client_socket)
    client_socket.close()

def client_thread(client_socket):
    username = None
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Client disconnected

            # first message == username
            if username is None:
                username = message
                clients[client_socket] = {"username": username, "channel": None}
                client_socket.send(f"Welcome {username}! You can now join a channel.".encode('utf-8'))
                continue

            # Commands
            if message.startswith("/join"):
                channel = message.split(':', 1)[1]
                if channel in channels:
                    if clients[client_socket]["channel"]:
                        channels[clients[client_socket]["channel"]].remove(client_socket)
                    clients[client_socket]["channel"] = channel
                    channels[channel].append(client_socket)
                    broadcast_to_channel(channel, f"{username} has joined {channel}")
                else:
                    client_socket.send(f"Channel {channel} does not exist.".encode('utf-8'))
            
            # private message
            elif message.startswith("/msg:"):
                parts = message.split(':', 2)
                if len(parts) == 3:
                    recipient_username = parts[1]
                    private_message = parts[2]
                    recipient_socket = next((client for client, info in clients.items() if info["username"] == recipient_username), None)
                    if recipient_socket:
                        recipient_socket.send(f"Private message from {username}: {private_message}".encode('utf-8'))
                    else:
                        client_socket.send(f"User {recipient_username} not found or offline.".encode('utf-8'))
                else:
                    client_socket.send("Invalid private message format.".encode('utf-8'))
            
            # group message broadcast to channel
            else:
                channel = clients[client_socket]["channel"]
                if channel:
                    broadcast_to_channel(channel, f"{username}: {message}")
                else:
                    client_socket.send("You are not in any channel.".encode('utf-8'))
        except Exception as e:
            print(f"Exception for {username}: {e}")
            break
    # exit
    remove_client(client_socket)
    if username:
        print(f"{username} disconnected.")

def start_server():
    # start server with configs
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Server is listening for connections...")

    # accept new client connections and start a new thread for each client
    while True:
        client_socket, _ = server_socket.accept()
        print("New connection established.")
        threading.Thread(target=client_thread, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
