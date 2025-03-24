import socket
import threading
import time

SERVER_IP = '172.20.10.3'  # e.g., 192.168.2.2 # hostname -I
PORT = 5000

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print("[Client] Server connection has ended.")
                break
            print(f"[Server] {message.decode()}")
        except:
            print("[Client] Lost connection with the server.")
            break

def send_messages(client_socket):
    while True:
        message = input("")
        if message.lower() == 'exit':
            print("[Client] Terminating connection.")
            client_socket.close()
            break
        client_socket.sendall(message.encode())

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print("[Client] Socket created successfully!")
    print(f"[Client] Attempting to connect to server ({SERVER_IP}:{PORT})...")
    time.sleep(1)

    try:
        client_socket.connect((SERVER_IP, PORT))
        print(f"[Client] Connected to server ({SERVER_IP}:{PORT}) successfully!")

        # Separate threads for receiving and sending messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        send_thread = threading.Thread(target=send_messages, args=(client_socket,))

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

    except Exception as e:
        print(f"[Client] Connection failed: {e}")
    finally:
        print("[Client] Exiting program.")
        client_socket.close()

if __name__ == "__main__":
    main()
