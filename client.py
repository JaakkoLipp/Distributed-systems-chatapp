import socket
import threading

def connect_to_server(username, addr):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((addr, 8080))
        client.send(username.encode('utf-8'))  # Send username after connecting
        return client
    except Exception as e:
        print(f"Failed to connect to the chat server: {e}")
        return None

def receive_messages(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print("\n\n           New message!\n##################################\n\n"+message+"\n\n##################################\n")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            client.close()
            break

def send_message(client_socket):
    while True:
        message = input("Type your message (or /quit): ")
        if message == "/quit":
            break
        client_socket.send(message.encode('utf-8'))

def private_message(client_socket):
    receiver = input("Recipient's username: ")
    print("Enter your private message below (type /quit to return to main menu):")
    while True:
        message = input("")
        if message == "/quit":
            break
        full_command = f"/msg:{receiver}:{message}"
        client_socket.send(full_command.encode('utf-8'))

def main():
    client_socket = None
    while True:
        if client_socket is None:
            # Connect
            server = input("Enter server IP (localhost): ")
            if (server == ""):
                server="localhost"
            username = input("Enter your username: ")
            if (username == ""):
                username="user"
            print(f"Welcome, {username}! Connecting to the chat server...")
            client_socket = connect_to_server(username, server)
            if client_socket:
                print("Connected! Now you can send and receive messages.")
                # Start thread for receiving messages
                threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
            else:
                print("Failed to connect, exiting...")
                break
        else:
            print("\n2. Send a private message")
            print("3. Join a text channel")
            print("4. Leave the server")
            choice = input("Choose an option: ")

            # Private Message
            if choice == '2':
                private_message(client_socket)
            # Join Channel
            elif choice == '3':
                print("channels:\ngeneral, testing and channel 3")
                channel = input("Channel name to join: ")
                client_socket.send(f"/join:{channel}".encode('utf-8'))
                send_message(client_socket)
            # Disconnect
            elif choice == '4':
                print("Leaving the chat...")
                client_socket.send("/disconnect".encode('utf-8'))
                client_socket.close()
                break
            else:
                print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
