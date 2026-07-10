import socket
import cv2
import time
import sys
import os


UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 7000

SHOW_PREVIEW = False


if len(sys.argv) < 2:
    print("[ERROR] Video path belum dikirim")
    sys.exit()


VIDEO_SOURCE = sys.argv[1]

if not os.path.exists(VIDEO_SOURCE):
    print("[ERROR] File video tidak ditemukan")
    print(VIDEO_SOURCE)
    sys.exit()


udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(VIDEO_SOURCE)

if not cap.isOpened():
    print("[ERROR] Video tidak bisa dibuka")
    print(VIDEO_SOURCE)
    sys.exit()


fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

delay = 1 / fps


print("[UDP VIDEO SENDER RUNNING]")
print(f"Video source : {VIDEO_SOURCE}")
print(f"Sending to   : {UDP_SERVER_IP}:{UDP_SERVER_PORT}")


try:
    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 360))

        success, encoded_frame = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 45]
        )

        if not success:
            continue

        data = encoded_frame.tobytes()

        if len(data) < 60000:
            udp_socket.sendto(
                data,
                (UDP_SERVER_IP, UDP_SERVER_PORT)
            )

        if SHOW_PREVIEW:
            cv2.imshow("UDP Sender", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        time.sleep(delay)

except KeyboardInterrupt:
    print("\n[STOPPED] UDP sender dihentikan")

finally:
    cap.release()
    udp_socket.close()
    cv2.destroyAllWindows()