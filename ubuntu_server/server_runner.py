import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TCP_SERVER = os.path.join(BASE_DIR, "tcp", "tcp_server.py")
UDP_RECEIVER = os.path.join(BASE_DIR, "udp", "udp_receiver.py")


def stop_process(process, process_name):
    if process.poll() is None:
        print(f"[STOP] Menghentikan {process_name}...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    print("=" * 60)
    print("NETWORK SERVER UBUNTU")
    print("=" * 60)
    print("[START] Menjalankan TCP Server port 6000")
    print("[START] Menjalankan UDP Receiver port 7000")
    print("[INFO] Tekan Ctrl + C untuk menghentikan server")
    print("=" * 60)

    tcp_process = subprocess.Popen([sys.executable, TCP_SERVER])
    udp_process = subprocess.Popen([sys.executable, UDP_RECEIVER])

    try:
        while True:
            if tcp_process.poll() is not None:
                print("[ERROR] TCP Server berhenti")
                break
            if udp_process.poll() is not None:
                print("[ERROR] UDP Receiver berhenti")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SERVER] Permintaan berhenti diterima")
    finally:
        stop_process(tcp_process, "TCP Server")
        stop_process(udp_process, "UDP Receiver")
        print("[SERVER] Semua layanan telah dihentikan")


if __name__ == "__main__":
    main()
