# Network App - TCP File Transfer & UDP Video Streaming

Network App adalah aplikasi web untuk mata kuliah Pemrograman Jaringan yang menerapkan konsep client-server. Aplikasi ini dibuat menggunakan Python Flask dan menggunakan beberapa protokol jaringan, yaitu HTTP, TCP, dan UDP.

Project ini memiliki dua fitur utama, yaitu transfer file menggunakan TCP dan streaming video menggunakan UDP. Selain itu, aplikasi juga dilengkapi dengan register, login, verifikasi OTP email, database MySQL, serta fitur CRUD untuk file dan video.

---

## Deskripsi Aplikasi

Aplikasi ini dibuat untuk mendemonstrasikan proses komunikasi data antara client dan server pada pemrograman jaringan.

Pada aplikasi ini, user dapat melakukan register dan login terlebih dahulu. Setelah login, user akan menerima kode OTP melalui email sebagai proses verifikasi. Setelah berhasil masuk ke dashboard, user dapat menggunakan dua fitur utama:

1. Upload File TCP
2. Streaming Video UDP

Fitur Upload File TCP digunakan untuk mengirim file dari website ke server menggunakan socket TCP. File yang berhasil dikirim akan disimpan pada folder server dan metadata file akan disimpan ke database MySQL.

Fitur Streaming Video UDP digunakan untuk mengupload video, memilih video yang ingin diputar, lalu video tersebut akan dikirim frame-by-frame menggunakan protokol UDP dan ditampilkan pada halaman website.

---

## Tujuan Project

Tujuan dari pembuatan aplikasi ini adalah:

- Memahami konsep komunikasi client-server.
- Mengimplementasikan komunikasi data menggunakan TCP, UDP, dan HTTP.
- Mengirim dan menerima data melalui jaringan.
- Mengimplementasikan socket programming pada Python.
- Menangani proses upload file dan streaming video.
- Menghubungkan aplikasi jaringan dengan database MySQL.
- Melakukan pengujian komunikasi antara client dan server.

---

## Teknologi yang Digunakan

| Teknologi | Keterangan |
|---|---|
| Python | Bahasa pemrograman utama |
| Flask | Framework web backend |
| HTML | Struktur halaman website |
| CSS | Tampilan antarmuka website |
| MySQL | Database untuk menyimpan data user, file, dan video |
| PyMySQL | Library koneksi Python ke MySQL |
| OpenCV | Library untuk membaca dan memproses video |
| Socket Programming | Digunakan untuk komunikasi TCP dan UDP |
| SMTP Gmail | Digunakan untuk mengirim kode OTP ke email |
| XAMPP | Digunakan untuk menjalankan MySQL secara lokal |
| GitHub | Digunakan untuk menyimpan source code project |

---

## Protokol Jaringan yang Digunakan

### 1. HTTP

HTTP digunakan untuk komunikasi antara browser client dan Flask server.

Contoh penggunaan HTTP pada aplikasi:

- Membuka halaman login
- Register akun
- Mengirim form login
- Mengupload file dari website
- Mengupload video dari website
- Menampilkan dashboard
- Menampilkan halaman upload TCP dan streaming UDP

---

### 2. TCP

TCP digunakan pada fitur upload file.

TCP dipilih karena proses pengiriman file membutuhkan data yang utuh, berurutan, dan reliable. Jika ada bagian file yang hilang, file dapat rusak atau tidak bisa dibuka. Oleh karena itu, TCP cocok digunakan untuk transfer file.

Alur komunikasi TCP pada aplikasi:

```text
User memilih file dari website
        ↓
Flask menerima file dari form upload
        ↓
Flask mengirim file ke TCP Server menggunakan socket TCP
        ↓
TCP Server menerima file
        ↓
File disimpan ke folder tcp/received_files/
        ↓
Metadata file disimpan ke database MySQL
```

---

### 3. UDP

UDP digunakan pada fitur streaming video.

UDP dipilih karena lebih ringan dan cepat untuk pengiriman data real-time. Pada streaming video, jika ada satu atau beberapa frame yang hilang, video masih tetap dapat berjalan.

Alur komunikasi UDP pada aplikasi:

```text
User upload video dari website
        ↓
Video disimpan ke folder udp/uploaded_videos/
        ↓
User memilih video untuk diputar
        ↓
UDP Sender membaca video frame-by-frame
        ↓
Frame video dikirim menggunakan UDP
        ↓
UDP Receiver menerima frame
        ↓
Frame ditampilkan pada halaman website
```

---

## Fitur Aplikasi

### 1. Register Akun

User dapat membuat akun baru dengan mengisi username, email, password, dan konfirmasi password. Data user akan disimpan ke database MySQL.

---

### 2. Login dan Verifikasi OTP

User dapat login menggunakan username dan password. Setelah login berhasil, sistem akan mengirimkan kode OTP ke email user. User harus memasukkan OTP yang benar agar dapat masuk ke dashboard.

---

### 3. Dashboard

Dashboard menampilkan informasi jumlah file TCP dan jumlah video UDP yang sudah diupload oleh user.

Dashboard juga menyediakan menu untuk mengakses:

- Upload File TCP
- Streaming Video UDP

---

### 4. Upload File TCP

Pada fitur Upload File TCP, user dapat:

- Mengupload file
- Mengirim file menggunakan TCP
- Melihat daftar file yang sudah diupload
- Mengubah nama file
- Menghapus file

File fisik disimpan di folder:

```text
tcp/received_files/
```

Metadata file disimpan di tabel:

```text
upload_history
```

---

### 5. Streaming Video UDP

Pada fitur Streaming Video UDP, user dapat:

- Mengupload video
- Melihat daftar video
- Mengubah nama video
- Menghapus video
- Memutar video menggunakan UDP
- Menghentikan video yang sedang diputar

Video fisik disimpan di folder:

```text
udp/uploaded_videos/
```

Metadata video disimpan di tabel:

```text
video_files
```

---

## Struktur Folder Project

```text
tugas-akhir/
│
├── app.py
├── db.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── verify.html
│   ├── dashboard.html
│   ├── upload.html
│   └── stream.html
│
├── static/
│   └── style.css
│
├── tcp/
│   ├── tcp_server.py
│   └── received_files/
│
├── udp/
│   ├── udp_sender.py
│   └── uploaded_videos/
│
└── uploads/
```

Folder berikut tidak perlu diupload ke GitHub karena berisi file hasil upload user:

```text
uploads/
tcp/received_files/
udp/uploaded_videos/
```

---

## Database

Database yang digunakan adalah MySQL.

Nama database yang digunakan:

```sql
pjar
```

### Tabel users

Tabel `users` digunakan untuk menyimpan data akun user.

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Tabel upload_history

Tabel `upload_history` digunakan untuk menyimpan metadata file yang dikirim menggunakan TCP.

```sql
CREATE TABLE upload_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100),
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### Tabel video_files

Tabel `video_files` digunakan untuk menyimpan metadata video yang digunakan pada fitur UDP streaming.

```sql
CREATE TABLE video_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    video_name VARCHAR(255) NOT NULL,
    video_path VARCHAR(255) NOT NULL,
    video_size BIGINT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Cara Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/username/nama-repository.git
cd nama-repository
```

---

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment di Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependency

```bash
pip install -r requirements.txt
```

Jika belum ada file `requirements.txt`, install library berikut secara manual:

```bash
pip install flask pymysql opencv-python python-dotenv werkzeug
```

---

### 4. Jalankan MySQL

Jalankan MySQL melalui XAMPP, lalu buka phpMyAdmin:

```text
http://localhost/phpmyadmin
```

Buat database dengan nama:

```sql
CREATE DATABASE pjar;
```

Setelah itu buat tabel `users`, `upload_history`, dan `video_files` sesuai struktur database yang sudah dijelaskan.

---

### 5. Buat File .env

Buat file `.env` di folder utama project.

Contoh isi file `.env`:

```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=pjar
```

Catatan:

- `EMAIL_PASSWORD` menggunakan Gmail App Password.
- Jangan menggunakan password Gmail biasa.
- File `.env` tidak perlu diupload ke GitHub.

---

### 6. Jalankan Aplikasi

```bash
python app.py
```

Setelah aplikasi berjalan, buka browser:

```text
http://127.0.0.1:5000
```

---

## Cara Menggunakan Aplikasi

### 1. Register

User membuat akun baru dengan memasukkan username, email, password, dan konfirmasi password.

---

### 2. Login

User login menggunakan username dan password yang sudah terdaftar.

---

### 3. Verifikasi OTP

Sistem mengirimkan kode OTP ke email user. User memasukkan kode OTP tersebut untuk masuk ke dashboard.

---

### 4. Upload File TCP

User masuk ke menu Upload File TCP, memilih file, lalu menekan tombol upload. File akan dikirim menggunakan TCP dan disimpan di server.

---

### 5. Streaming Video UDP

User masuk ke menu Streaming Video UDP, mengupload video, lalu menekan tombol Putar Video. Video akan dikirim frame-by-frame menggunakan UDP dan ditampilkan pada website.

---

## Mekanisme Client-Server

Aplikasi ini memiliki beberapa proses komunikasi client-server.

### Browser Client dan Flask Server

Browser berperan sebagai client yang mengirim request HTTP ke Flask server. Flask server memproses request dan mengembalikan response berupa halaman web.

### Flask dan TCP Server

Pada fitur upload file, Flask mengirim file ke TCP Server menggunakan socket TCP. TCP Server menerima file dan menyimpannya di folder server.

### UDP Sender dan UDP Receiver

Pada fitur streaming video, UDP Sender membaca video frame-by-frame lalu mengirim frame ke UDP Receiver. Frame yang diterima akan ditampilkan pada halaman website.

---

## Error Handling

Aplikasi menangani beberapa kemungkinan error, seperti:

- Username atau password salah
- OTP salah
- Email gagal dikirim
- File belum dipilih
- Video belum dipilih
- Format video tidak didukung
- File gagal dikirim melalui TCP
- Video tidak ditemukan
- Database gagal terhubung
- File atau video gagal dihapus

Pesan error akan ditampilkan pada halaman website agar user mengetahui masalah yang terjadi.

---

## Kelebihan Aplikasi

Beberapa kelebihan aplikasi ini adalah:

- Menggunakan konsep client-server.
- Menggunakan lebih dari satu protokol jaringan, yaitu HTTP, TCP, dan UDP.
- Memiliki fitur transfer file menggunakan TCP.
- Memiliki fitur streaming video menggunakan UDP.
- Memiliki sistem register, login, dan OTP email.
- Menggunakan database MySQL untuk menyimpan data.
- Memiliki fitur CRUD untuk file dan video.
- Tampilan aplikasi dibuat berbasis web sehingga mudah digunakan.

---

## Kekurangan Aplikasi

Beberapa kekurangan aplikasi ini adalah:

- UDP streaming hanya mengirim frame video tanpa audio.
- Aplikasi masih berjalan pada server lokal.
- Belum menggunakan HTTPS.
- Belum ada fitur role admin dan user.
- Penyimpanan file masih menggunakan folder server lokal.
- Belum menggunakan cloud storage untuk file berukuran besar.

---

## Pengembangan Selanjutnya

Aplikasi ini masih dapat dikembangkan dengan beberapa fitur tambahan, seperti:

- Menambahkan HTTPS agar komunikasi lebih aman.
- Menambahkan role admin dan user.
- Menambahkan batas ukuran upload file dan video.
- Menambahkan cloud storage untuk menyimpan file dan video.
- Menambahkan fitur audio pada UDP streaming.
- Menambahkan monitoring koneksi client-server.
- Melakukan deployment ke server publik.
- Menghubungkan domain menggunakan Cloudflare DNS.

---

## Kesimpulan

Network App merupakan aplikasi pemrograman jaringan berbasis web yang menerapkan konsep client-server dengan menggunakan protokol HTTP, TCP, dan UDP.

TCP digunakan pada fitur transfer file karena membutuhkan pengiriman data yang reliable, utuh, dan berurutan. UDP digunakan pada fitur streaming video karena lebih ringan dan cocok untuk pengiriman data real-time. HTTP digunakan untuk komunikasi antara browser dan Flask server.

Dengan aplikasi ini, proses komunikasi jaringan seperti pengiriman data, penerimaan data, socket programming, database, dan error handling dapat diimplementasikan dalam satu sistem aplikasi.

---

## Author

Nama: Muhammad Ferdi  
Mata Kuliah: Pemrograman Jaringan  
Project: Network App - TCP File Transfer & UDP Video Streaming
