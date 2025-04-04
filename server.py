# server2.py
import socket
import threading
import json
from RCController import process_command

def client_handler(client_socket, address):
    print(f"[Server] Connection from {address}")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Close the connection if no data is received
            try:
                # Try parsing as JSON (expecting command in JSON format)
                try:
                    message = json.loads(data.decode())
                    command = message.get("command", "")
                except json.JSONDecodeError:
                    command = data.decode().strip()
                print(f"[Server] Received command: {command}")
                process_command(command)
            except Exception as e:
                print(f"[Server] Error processing command: {e}")
    except Exception as e:
        print(f"[Server] Connection error: {e}")
    finally:
        print(f"[Server] Connection closed: {address}")
        client_socket.close()

def start_server(host="0.0.0.0", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[Server] Listening on {host}:{port}")
    try:
        while True:
            client_sock, addr = server_socket.accept()
            threading.Thread(target=client_handler, args=(client_sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("[Server] Shutting down")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()