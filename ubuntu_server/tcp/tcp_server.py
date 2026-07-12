import os
import socket
import struct
import threading

TCP_HOST = "0.0.0.0"
TCP_PORT = 6000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECEIVED_FOLDER = os.path.join(BASE_DIR, "received_files")
os.makedirs(RECEIVED_FOLDER, exist_ok=True)


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
        print(f"\n[TCP CONNECTED] Client: {address}")

        filename_length_data = receive_exact(client_socket, 4)
        if not filename_length_data:
            print("[TCP ERROR] Panjang nama file tidak diterima")
            return

        filename_length = struct.unpack("!I", filename_length_data)[0]
        filename_data = receive_exact(client_socket, filename_length)
        if not filename_data:
            print("[TCP ERROR] Nama file tidak diterima")
            return

        filename = os.path.basename(filename_data.decode("utf-8"))

        filesize_data = receive_exact(client_socket, 8)
        if not filesize_data:
            print("[TCP ERROR] Ukuran file tidak diterima")
            return

        filesize = struct.unpack("!Q", filesize_data)[0]
        filepath = os.path.join(RECEIVED_FOLDER, filename)

        print(f"[TCP RECEIVING] Nama file : {filename}")
        print(f"[TCP RECEIVING] Ukuran    : {filesize} bytes")
        print(f"[TCP RECEIVING] Dari      : {address[0]}")

        received_size = 0
        with open(filepath, "wb") as file:
            while received_size < filesize:
                remaining_size = filesize - received_size
                data = client_socket.recv(min(4096, remaining_size))
                if not data:
                    break
                file.write(data)
                received_size += len(data)

        if received_size == filesize:
            print(f"[TCP SUCCESS] File tersimpan: {filepath}")
            print(f"[TCP SUCCESS] Total diterima: {received_size} bytes")
            client_socket.sendall(b"FILE_RECEIVED")
        else:
            print("[TCP ERROR] File tidak diterima secara lengkap")
            print(f"[TCP ERROR] Diterima: {received_size}/{filesize} bytes")
            client_socket.sendall(b"FILE_INCOMPLETE")

    except Exception as error:
        print(f"[TCP SERVER ERROR] {error}")
        try:
            client_socket.sendall(b"SERVER_ERROR")
        except Exception:
            pass
    finally:
        client_socket.close()
        print(f"[TCP DISCONNECTED] Client: {address}")


def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((TCP_HOST, TCP_PORT))
    server_socket.listen(5)

    print("=" * 55)
    print("TCP FILE SERVER UBUNTU")
    print("=" * 55)
    print(f"[TCP SERVER RUNNING] {TCP_HOST}:{TCP_PORT}")
    print(f"[SAVE FOLDER] {RECEIVED_FOLDER}")
    print("[STATUS] Menunggu koneksi dari client Windows...")
    print("=" * 55)

    try:
        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        print("\n[TCP SERVER] Server dihentikan")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_tcp_server()
