from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, abort
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import random
import smtplib
from email.message import EmailMessage
import socket
import os
import struct
import threading
import subprocess
import sys
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret_key_tugas_akhir")


# =========================
# KONFIGURASI EMAIL
# =========================
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# =========================
# KONFIGURASI TCP
# =========================
TCP_HOST = "127.0.0.1"
TCP_PORT = 6000

UPLOAD_FOLDER = "uploads"

TCP_RECEIVED_FOLDER = os.path.join("tcp", "received_files")

VIDEO_UPLOAD_FOLDER = os.path.join("udp", "uploaded_videos")
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

# =========================
# KONFIGURASI UDP
# =========================
UDP_HOST = "0.0.0.0"
UDP_PORT = 7000

udp_process = None
# =========================
# BUAT FOLDER UPLOAD JIKA BELUM ADA
# =========================
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(TCP_RECEIVED_FOLDER):
    os.makedirs(TCP_RECEIVED_FOLDER)
if not os.path.exists(VIDEO_UPLOAD_FOLDER):
    os.makedirs(VIDEO_UPLOAD_FOLDER)


def resolve_project_path(path):
    """Mengubah path relatif dari database menjadi path absolut project."""
    if os.path.isabs(path):
        return os.path.normpath(path)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_dir, path))


# =========================
# ROUTE UTAMA
# =========================
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================
# FUNCTION KIRIM OTP EMAIL
# =========================
def send_otp_email(to_email, otp_code):
    msg = EmailMessage()
    msg["Subject"] = "Kode Verifikasi Login"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(
        f"""
Halo,

Kode verifikasi login kamu adalah:

{otp_code}

Jangan berikan kode ini kepada orang lain.
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Password dan konfirmasi password tidak sama")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        try:
            connection = get_db_connection()

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO users (username, email, password)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (username, email, hashed_password))

            connection.commit()
            connection.close()

            flash("Akun berhasil dibuat, silakan login")
            return redirect(url_for("login"))

        except Exception as error:
            flash("Gagal daftar: username atau email mungkin sudah digunakan")
            print("[REGISTER ERROR]", error)

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            connection = get_db_connection()

            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()

            connection.close()

        except Exception as error:
            flash("Gagal terhubung ke database")
            print("[LOGIN DB ERROR]", error)
            return redirect(url_for("login"))

        if user and check_password_hash(user["password"], password):
            otp_code = str(random.randint(100000, 999999))

            session["temp_user_id"] = user["id"]
            session["temp_username"] = user["username"]
            session["temp_email"] = user["email"]
            session["otp_code"] = otp_code

            try:
                send_otp_email(user["email"], otp_code)

                flash("Kode OTP sudah dikirim ke email")
                return redirect(url_for("verify"))

            except Exception as error:
                flash("Gagal mengirim OTP ke email")
                print("[EMAIL ERROR]", error)
                return redirect(url_for("login"))

        else:
            flash("Username atau password salah")

    return render_template("login.html")


# =========================
# VERIFY OTP
# =========================
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if "temp_username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        input_otp = request.form["otp"]

        if input_otp == session.get("otp_code"):
            session["user_id"] = session["temp_user_id"]
            session["username"] = session["temp_username"]
            session["email"] = session["temp_email"]

            session.pop("temp_user_id", None)
            session.pop("temp_username", None)
            session.pop("temp_email", None)
            session.pop("otp_code", None)

            return redirect(url_for("dashboard"))

        else:
            flash("Kode OTP salah")

    return render_template("verify.html")

def get_dashboard_stats(user_id):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total_files FROM upload_history WHERE user_id = %s",
            (user_id,)
        )
        file_result = cursor.fetchone()

        cursor.execute(
            "SELECT COUNT(*) AS total_videos FROM video_files WHERE user_id = %s",
            (user_id,)
        )
        video_result = cursor.fetchone()

    connection.close()

    return {
        "total_files": file_result["total_files"],
        "total_videos": video_result["total_videos"]
    }

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    if "user_id" not in session:
        session.clear()
        return redirect(url_for("login"))

    stats = get_dashboard_stats(session["user_id"])

    return render_template(
        "dashboard.html",
        username=session["username"],
        stats=stats
    )


# =========================
# FUNCTION KIRIM FILE KE TCP SERVER
# =========================
def send_file_to_tcp_server(filepath, tcp_filename):
    filesize = os.path.getsize(filepath)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((TCP_HOST, TCP_PORT))

    filename_data = tcp_filename.encode()

    # Kirim panjang nama file
    client_socket.sendall(
        struct.pack("!I", len(filename_data))
    )

    # Kirim nama file unik ke TCP Server
    client_socket.sendall(filename_data)

    # Kirim ukuran file
    client_socket.sendall(
        struct.pack("!Q", filesize)
    )

    # Kirim isi file
    with open(filepath, "rb") as file:
        while True:
            data = file.read(4096)

            if not data:
                break

            client_socket.sendall(data)

    response = client_socket.recv(1024).decode()

    client_socket.close()

    return response

def receive_exact(client_socket, size):
    data = b""

    while len(data) < size:
        packet = client_socket.recv(size - len(data))

        if not packet:
            return None

        data += packet

    return data


def handle_tcp_client(client_socket, address):
    try:
        print(f"[TCP CONNECTED] {address}")

        filename_length_data = receive_exact(client_socket, 4)

        if not filename_length_data:
            print("[TCP ERROR] Gagal menerima panjang nama file")
            return

        filename_length = struct.unpack("!I", filename_length_data)[0]

        filename_data = receive_exact(client_socket, filename_length)

        if not filename_data:
            print("[TCP ERROR] Gagal menerima nama file")
            return

        filename = filename_data.decode()

        filesize_data = receive_exact(client_socket, 8)

        if not filesize_data:
            print("[TCP ERROR] Gagal menerima ukuran file")
            return

        filesize = struct.unpack("!Q", filesize_data)[0]

        filepath = os.path.join(TCP_RECEIVED_FOLDER, filename)

        print(f"[TCP RECEIVING] {filename} ({filesize} bytes)")

        received_size = 0

        with open(filepath, "wb") as file:
            while received_size < filesize:
                data = client_socket.recv(4096)

                if not data:
                    break

                file.write(data)
                received_size += len(data)

        print(f"[TCP SUCCESS] File saved: {filepath}")

        client_socket.send("FILE_RECEIVED".encode())

    except Exception as error:
        print("[TCP SERVER ERROR]", error)

    finally:
        client_socket.close()


def start_tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        tcp_socket.bind((TCP_HOST, TCP_PORT))
        tcp_socket.listen(5)

        print(f"[TCP SERVER RUNNING] {TCP_HOST}:{TCP_PORT}")

        while True:
            client_socket, address = tcp_socket.accept()

            thread = threading.Thread(
                target=handle_tcp_client,
                args=(client_socket, address),
                daemon=True
            )

            thread.start()

    except OSError as error:
        print("[TCP SERVER WARNING]", error)
        print("Kemungkinan TCP Server sudah berjalan di port yang sama.")

# =========================
# SIMPAN HISTORY UPLOAD KE DATABASE
# =========================
def save_upload_history(user_id, filename, file_size, file_type, file_path):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            INSERT INTO upload_history
            (user_id, filename, file_size, file_type, file_path)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (user_id, filename, file_size, file_type, file_path)
        )

    connection.commit()
    connection.close()

def format_file_size(size):
    size = int(size)

    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"

# =========================
# AMBIL HISTORY UPLOAD DARI DATABASE
# =========================
def get_upload_history(user_id):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            SELECT id, filename, file_size, file_type, file_path, uploaded_at
            FROM upload_history
            WHERE user_id = %s
            ORDER BY uploaded_at DESC
        """

        cursor.execute(sql, (user_id,))
        history = cursor.fetchall()

    connection.close()

    for item in history:
        item["formatted_size"] = format_file_size(item["file_size"])

    return history

def get_tcp_file_by_id(file_id, user_id):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            SELECT id, filename, file_path
            FROM upload_history
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(sql, (file_id, user_id))
        file_data = cursor.fetchone()

    connection.close()

    return file_data


def update_tcp_filename(file_id, user_id, new_filename):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            UPDATE upload_history
            SET filename = %s
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(sql, (new_filename, file_id, user_id))

    connection.commit()
    connection.close()


def delete_tcp_file(file_id, user_id):
    file_data = get_tcp_file_by_id(file_id, user_id)

    if not file_data:
        return False

    file_path = file_data["file_path"]

    if os.path.exists(file_path):
        os.remove(file_path)

    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            DELETE FROM upload_history
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(sql, (file_id, user_id))

    connection.commit()
    connection.close()

    return True

# =========================
# ROUTE UPLOAD TCP
# =========================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "username" not in session:
        return redirect(url_for("login"))

    if "user_id" not in session:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if uploaded_file is None or uploaded_file.filename == "":
            flash("File belum dipilih")
            return redirect(url_for("upload"))

        original_filename = secure_filename(uploaded_file.filename)

        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        uploaded_file.save(filepath)

        file_size = os.path.getsize(filepath)
        file_type = uploaded_file.content_type

        try:
            response = send_file_to_tcp_server(filepath, unique_filename)

            if response == "FILE_RECEIVED":
                tcp_saved_path = os.path.join(
                    "tcp",
                    "received_files",
                    unique_filename
                ).replace("\\", "/")

                save_upload_history(
                    session["user_id"],
                    original_filename,
                    file_size,
                    file_type,
                    tcp_saved_path
                )

                flash("File berhasil dikirim via TCP dan tercatat di database")

            else:
                flash("File gagal dikirim ke TCP Server")

        except Exception as error:
            flash(f"Error TCP: {error}")
            print("[TCP UPLOAD ERROR]", error)

        return redirect(url_for("upload"))

    upload_history = get_upload_history(session["user_id"])

    return render_template(
        "upload.html",
        username=session["username"],
        upload_history=upload_history
    )

@app.route("/update_tcp_file/<int:file_id>", methods=["POST"])
def update_tcp_file(file_id):
    if "username" not in session:
        return redirect(url_for("login"))

    new_filename = request.form["filename"]

    if new_filename.strip() == "":
        flash("Nama file tidak boleh kosong")
        return redirect(url_for("upload"))

    update_tcp_filename(
        file_id,
        session["user_id"],
        new_filename
    )

    flash("Nama file berhasil diperbarui")
    return redirect(url_for("upload"))

@app.route("/delete_tcp_file/<int:file_id>", methods=["POST"])
def delete_tcp_file_route(file_id):
    if "username" not in session:
        return redirect(url_for("login"))

    success = delete_tcp_file(file_id, session["user_id"])

    if success:
        flash("File berhasil dihapus")
    else:
        flash("File tidak ditemukan")

    return redirect(url_for("upload"))

# =========================
# UDP RECEIVER
# =========================
def start_udp_receiver():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        udp_socket.bind((UDP_HOST, UDP_PORT))
        print(f"[UDP RECEIVER RUNNING] {UDP_HOST}:{UDP_PORT}")

        frame_count = 0

        while True:
            data, address = udp_socket.recvfrom(65535)
            frame_count += 1

            if frame_count == 1:
                print(f"[UDP RECEIVER] Paket pertama diterima dari {address}")

    except OSError as error:
        print("[UDP RECEIVER WARNING]", error)
        print("Kemungkinan UDP Receiver sudah berjalan di port yang sama.")

    except Exception as error:
        print("[UDP RECEIVER ERROR]", error)

    finally:
        udp_socket.close()


def allowed_video_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


def save_video_file(user_id, video_name, video_path, video_size):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            INSERT INTO video_files
            (user_id, video_name, video_path, video_size)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, video_name, video_path, video_size))

    connection.commit()
    connection.close()


def get_video_files(user_id):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            SELECT id, video_name, video_path, video_size, uploaded_at
            FROM video_files
            WHERE user_id = %s
            ORDER BY uploaded_at DESC
        """
        cursor.execute(sql, (user_id,))
        videos = cursor.fetchall()

    connection.close()

    for video in videos:
        video["formatted_size"] = format_file_size(video["video_size"])

    return videos


def get_video_by_id(video_id, user_id):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            SELECT id, video_name, video_path
            FROM video_files
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(sql, (video_id, user_id))
        video = cursor.fetchone()

    connection.close()
    return video

def update_video_name(video_id, user_id, new_video_name):
    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            UPDATE video_files
            SET video_name = %s
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(sql, (new_video_name, video_id, user_id))

    connection.commit()
    connection.close()


def delete_video_file(video_id, user_id):
    video = get_video_by_id(video_id, user_id)

    if not video:
        return False

    video_path = resolve_project_path(video["video_path"])

    if os.path.exists(video_path):
        os.remove(video_path)

    connection = get_db_connection()

    with connection.cursor() as cursor:
        sql = """
            DELETE FROM video_files
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(sql, (video_id, user_id))

    connection.commit()
    connection.close()

    return True

def stop_udp_sender():
    global udp_process

    if udp_process and udp_process.poll() is None:
        udp_process.terminate()

        try:
            udp_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            udp_process.kill()

    udp_process = None


def start_udp_sender(video_path):
    global udp_process

    stop_udp_sender()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sender_script = os.path.join(base_dir, "udp", "udp_sender.py")
    video_path_abs = resolve_project_path(video_path)

    if not os.path.exists(sender_script):
        raise FileNotFoundError("File udp_sender.py tidak ditemukan")

    if not os.path.exists(video_path_abs):
        raise FileNotFoundError("File video tidak ditemukan di folder uploaded_videos")

    udp_process = subprocess.Popen(
        [sys.executable, sender_script, video_path_abs],
        cwd=base_dir
    )


# =========================
# ROUTE STREAM
# =========================
@app.route("/stream")
def stream():
    if "user_id" not in session:
        return redirect(url_for("login"))

    videos = get_video_files(session["user_id"])
    active_video = None
    current_video_id = session.get("current_video_id")

    if current_video_id:
        active_video = next(
            (video for video in videos if video["id"] == current_video_id),
            None
        )

        if active_video is None:
            stop_udp_sender()
            session.pop("current_video_id", None)
            session.pop("current_video_name", None)

    return render_template(
        "stream.html",
        username=session["username"],
        videos=videos,
        active_video=active_video
    )


@app.route("/upload_video", methods=["POST"])
def upload_video():
    if "username" not in session:
        return redirect(url_for("login"))

    uploaded_video = request.files.get("video")

    if uploaded_video is None or uploaded_video.filename == "":
        flash("Video belum dipilih")
        return redirect(url_for("stream"))

    if not allowed_video_file(uploaded_video.filename):
        flash("Format video tidak didukung. Gunakan mp4, avi, mov, atau mkv")
        return redirect(url_for("stream"))

    original_filename = secure_filename(uploaded_video.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()

    unique_filename = f"{uuid.uuid4().hex}.{extension}"

    video_path = os.path.join(
        VIDEO_UPLOAD_FOLDER,
        unique_filename
    )

    uploaded_video.save(video_path)

    video_size = os.path.getsize(video_path)

    save_video_file(
        session["user_id"],
        original_filename,
        video_path.replace("\\", "/"),
        video_size
    )

    flash("Video berhasil diupload dan tersimpan di database")
    return redirect(url_for("stream"))

@app.route("/update_video/<int:video_id>", methods=["POST"])
def update_video(video_id):
    if "username" not in session:
        return redirect(url_for("login"))

    new_video_name = request.form["video_name"]

    if new_video_name.strip() == "":
        flash("Nama video tidak boleh kosong")
        return redirect(url_for("stream") + "#video-library")

    update_video_name(
        video_id,
        session["user_id"],
        new_video_name
    )

    flash("Nama video berhasil diperbarui")
    return redirect(url_for("stream") + "#video-library")

@app.route("/delete_video/<int:video_id>", methods=["POST"])
def delete_video(video_id):
    if "username" not in session:
        return redirect(url_for("login"))

    video = get_video_by_id(video_id, session["user_id"])

    if not video:
        flash("Video tidak ditemukan")
        return redirect(url_for("stream") + "#video-library")

    if session.get("current_video_id") == video_id:
        stop_udp_sender()
        session.pop("current_video_id", None)
        session.pop("current_video_name", None)

    success = delete_video_file(video_id, session["user_id"])

    if success:
        flash("Video berhasil dihapus")
    else:
        flash("Gagal menghapus video")

    return redirect(url_for("stream") + "#video-library")

@app.route("/start_stream/<int:video_id>", methods=["POST"])
def start_stream(video_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    video = get_video_by_id(video_id, session["user_id"])

    if not video:
        flash("Video tidak ditemukan")
        return redirect(url_for("stream") + "#video-library")

    video_path = resolve_project_path(video["video_path"])

    if not os.path.exists(video_path):
        flash("File video tidak ditemukan di folder uploaded_videos")
        return redirect(url_for("stream") + "#video-library")

    try:
        # Proses sender UDP tetap dijalankan untuk komunikasi UDP.
        start_udp_sender(video_path)

        # ID video disimpan agar player HTML5 dapat menampilkan video
        # lengkap dengan play, pause, suara, durasi, dan fullscreen.
        session["current_video_id"] = video["id"]
        session["current_video_name"] = video["video_name"]

        flash(f"Video siap diputar: {video['video_name']}")

    except Exception as error:
        flash(f"Gagal memulai video: {error}")
        print("[START STREAM ERROR]", repr(error))

    return redirect(url_for("stream") + "#player")


@app.route("/stop_stream", methods=["POST"])
def stop_stream():
    if "user_id" not in session:
        return redirect(url_for("login"))

    stop_udp_sender()

    session.pop("current_video_id", None)
    session.pop("current_video_name", None)

    flash("Pemutaran video dihentikan")
    return redirect(url_for("stream") + "#player")


# =========================
# KIRIM FILE VIDEO KE PLAYER HTML5
# =========================
@app.route("/video-file/<int:video_id>")
def video_file(video_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    video = get_video_by_id(video_id, session["user_id"])

    if not video:
        abort(404)

    video_path = resolve_project_path(video["video_path"])

    if not os.path.exists(video_path):
        abort(404)

    return send_file(
        video_path,
        conditional=True
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    if session.get("current_video_id"):
        stop_udp_sender()

    session.clear()
    return redirect(url_for("login"))


# =========================
# JALANKAN APP
# =========================
if __name__ == "__main__":
    threading.Thread(
        target=start_udp_receiver,
        daemon=True
    ).start()

    threading.Thread(
        target=start_tcp_server,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )