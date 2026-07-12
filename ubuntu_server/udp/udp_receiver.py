import os
import socket
import time

UDP_HOST = "0.0.0.0"
UDP_PORT = 7000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECEIVED_FOLDER = os.path.join(BASE_DIR, "received_frames")
LATEST_FRAME_PATH = os.path.join(RECEIVED_FOLDER, "latest_frame.jpg")
os.makedirs(RECEIVED_FOLDER, exist_ok=True)


def start_udp_receiver():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_HOST, UDP_PORT))

    print("=" * 60)
    print("UDP VIDEO RECEIVER UBUNTU")
    print("=" * 60)
    print(f"[UDP RECEIVER RUNNING] {UDP_HOST}:{UDP_PORT}")
    print(f"[SAVE FOLDER] {RECEIVED_FOLDER}")
    print("[STATUS] Menunggu paket UDP dari Windows...")
    print("=" * 60)

    packet_count = 0
    total_bytes = 0
    last_report_time = time.time()
    current_client = None

    try:
        while True:
            data, address = udp_socket.recvfrom(65535)
            packet_count += 1
            total_bytes += len(data)

            if current_client != address:
                current_client = address
                print()
                print(f"[UDP CLIENT] Paket diterima dari {address[0]}:{address[1]}")

            if data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"):
                with open(LATEST_FRAME_PATH, "wb") as frame_file:
                    frame_file.write(data)

            current_time = time.time()
            if current_time - last_report_time >= 1:
                print(
                    f"[UDP RECEIVING] Paket: {packet_count} | "
                    f"Total: {total_bytes} bytes | Client: {address[0]}"
                )
                last_report_time = current_time

    except KeyboardInterrupt:
        print("\n[UDP RECEIVER] Server dihentikan")
    except Exception as error:
        print(f"[UDP RECEIVER ERROR] {error}")
    finally:
        udp_socket.close()
        print("[UDP RECEIVER] Socket ditutup")


if __name__ == "__main__":
    start_udp_receiver()
