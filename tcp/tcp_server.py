import socket
import os
import struct
import threading

HOST = "0.0.0.0"
PORT = 6000

RECEIVED_FOLDER = "received_files"

if not os.path.exists(RECEIVED_FOLDER):
    os.makedirs(RECEIVED_FOLDER)


def receive_exact(client_socket, size):
    data = b""

    while len(data) < size:
        packet = client_socket.recv(size - len(data))

        if not packet:
            return None

        data += packet

    return data


def handle_client(client_socket, address):
    try:
        print(f"[CONNECTED] {address}")

        # Terima panjang nama file
        filename_length_data = receive_exact(client_socket, 4)
        filename_length = struct.unpack("!I", filename_length_data)[0]

        # Terima nama file
        filename_data = receive_exact(client_socket, filename_length)
        filename = filename_data.decode()

        # Terima ukuran file
        filesize_data = receive_exact(client_socket, 8)
        filesize = struct.unpack("!Q", filesize_data)[0]

        filepath = os.path.join(RECEIVED_FOLDER, filename)

        print(f"[RECEIVING] {filename} ({filesize} bytes)")

        received_size = 0

        with open(filepath, "wb") as file:
            while received_size < filesize:
                data = client_socket.recv(4096)

                if not data:
                    break

                file.write(data)
                received_size += len(data)

        print(f"[SUCCESS] File saved: {filepath}")

        client_socket.send("FILE_RECEIVED".encode())

    except Exception as error:
        print(f"[ERROR] {error}")

    finally:
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[TCP SERVER RUNNING] {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address)
        )

        thread.start()


if __name__ == "__main__":
    start_server()