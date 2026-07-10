
````markdown
# Network App — TCP File Transfer & UDP Video Streaming

Network App adalah aplikasi web berbasis **Pemrograman Jaringan** yang menerapkan konsep **client-server** menggunakan beberapa protokol jaringan, yaitu **HTTP**, **TCP**, dan **UDP**.

Aplikasi ini dibuat untuk memenuhi tugas mata kuliah Pemrograman Jaringan dengan fokus utama pada proses komunikasi data antar client dan server.

---

## Deskripsi Singkat

Aplikasi ini memiliki dua fitur utama:

1. **Upload File menggunakan TCP**
   - User dapat mengupload file melalui website.
   - File dikirim menggunakan socket TCP.
   - File diterima oleh TCP Server dan disimpan pada folder server.
   - Metadata file seperti nama file, ukuran, tipe file, dan lokasi file disimpan ke database MySQL.

2. **Streaming Video menggunakan UDP**
   - User dapat mengupload video melalui website.
   - Video disimpan pada server dan datanya dicatat ke database.
   - User dapat memilih video untuk diputar.
   - Video dikirim frame-by-frame menggunakan protokol UDP dan ditampilkan pada halaman website.

Selain itu, aplikasi juga memiliki fitur:
- Register akun
- Login
- Verifikasi OTP melalui email
- Dashboard statistik
- CRUD file TCP
- CRUD video UDP
- Tampilan web modern dan responsif

---

## Tujuan Project

Project ini dibuat untuk memahami dan mengimplementasikan konsep:

- Komunikasi jaringan berbasis client-server
- Pengiriman data melalui protokol TCP
- Pengiriman data melalui protokol UDP
- Komunikasi web menggunakan HTTP
- Manajemen koneksi socket
- Pengolahan file dan video
- Penyimpanan metadata menggunakan database MySQL
- Error handling pada aplikasi jaringan

---

## Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Bahasa pemrograman utama |
| Flask | Framework web backend |
| HTML | Struktur halaman web |
| CSS | Tampilan antarmuka aplikasi |
| MySQL | Database aplikasi |
| PyMySQL | Koneksi Python ke MySQL |
| OpenCV | Membaca dan memproses frame video |
| Socket Programming | Implementasi TCP dan UDP |
| SMTP Gmail | Mengirim kode OTP ke email |
| XAMPP | Menjalankan MySQL secara lokal |
| Git & GitHub | Version control dan repository |

---

## Protokol yang Digunakan

### 1. HTTP

HTTP digunakan untuk komunikasi antara browser client dengan Flask web server.

Contoh:
- Membuka halaman login
- Register akun
- Mengupload file dari form website
- Mengupload video dari form website
- Menampilkan dashboard

---

### 2. TCP

TCP digunakan pada fitur **File Transfer**.

Alasan menggunakan TCP:
- TCP menjamin data sampai secara utuh.
- Data dikirim secara berurutan.
- Cocok untuk pengiriman file karena file tidak boleh rusak atau hilang sebagian.

Alur TCP pada aplikasi:

```text
User upload file dari browser
        ↓
Flask menerima file
        ↓
Flask mengirim file ke TCP Server menggunakan socket TCP
        ↓
TCP Server menerima file
        ↓
File disimpan ke folder tcp/received_files/
        ↓
Metadata file disimpan ke MySQL
````

---

### 3. UDP

UDP digunakan pada fitur **Video Streaming**.

Alasan menggunakan UDP:

* UDP lebih ringan dan cepat.
* Cocok untuk data real-time seperti video streaming.
* Jika ada frame yang hilang, video masih tetap bisa berjalan.

Alur UDP pada aplikasi:

```text
User upload video dari website
        ↓
Video disimpan ke folder udp/uploaded_videos/
        ↓
User memilih video untuk diputar
        ↓
UDP Sender membaca video frame-by-frame
        ↓
Frame dikirim ke UDP Receiver
        ↓
Flask menampilkan frame video ke website
```

---

## Fitur Aplikasi

### 1. Register Akun

User dapat membuat akun baru dengan mengisi:

* Username
* Email
* Password
* Konfirmasi password

Data akun disimpan ke database MySQL.

---

### 2. Login dan OTP Email

Setelah login menggunakan username dan password, sistem akan mengirimkan kode OTP ke email user.

User harus memasukkan OTP dengan benar agar dapat masuk ke dashboard.

---

### 3. Dashboard

Dashboard menampilkan:

* Total file TCP yang sudah diupload
* Total video UDP yang sudah diupload
* Menu menuju fitur Upload File TCP
* Menu menuju fitur Streaming Video UDP

---

### 4. Upload File TCP

Pada fitur ini user dapat:

* Mengupload file
* Mengirim file menggunakan TCP
* Melihat daftar file yang sudah diupload
* Mengubah nama file
* Menghapus file

File fisik disimpan pada folder:

```text
tcp/received_files/
```

Metadata file disimpan pada tabel:

```text
upload_history
```

---

### 5. Streaming Video UDP

Pada fitur ini user dapat:

* Mengupload video
* Melihat daftar video
* Mengubah nama video
* Menghapus video
* Memutar video menggunakan UDP streaming
* Menghentikan video yang sedang diputar

Video fisik disimpan pada folder:

```text
udp/uploaded_videos/
```

Metadata video disimpan pada tabel:

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

Catatan:

Folder berikut tidak perlu dimasukkan ke GitHub karena berisi file hasil upload user:

```text
uploads/
tcp/received_files/
udp/uploaded_videos/
```

---

## Database

Database yang digunakan adalah MySQL.

Nama database:

```sql
pjar
```

### Tabel `users`

Digunakan untuk menyimpan data akun user.

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

### Tabel `upload_history`

Digunakan untuk menyimpan metadata file TCP.

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

### Tabel `video_files`

Digunakan untuk menyimpan metadata video UDP.

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

## Cara Instalasi dan Menjalankan Project

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

### 3. Install Library

```bash
pip install -r requirements.txt
```

Jika belum memiliki `requirements.txt`, install manual:

```bash
pip install flask pymysql opencv-python python-dotenv werkzeug
```

---

### 4. Buat Database MySQL

Jalankan MySQL melalui XAMPP, lalu buka:

```text
http://localhost/phpmyadmin
```

Buat database:

```sql
CREATE DATABASE pjar;
```

Kemudian buat tabel `users`, `upload_history`, dan `video_files` sesuai SQL di bagian Database.

---

### 5. Buat File `.env`

Buat file `.env` di folder utama project.

Contoh isi:

```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=pjar
```

Catatan:

* `EMAIL_PASSWORD` menggunakan Gmail App Password, bukan password Gmail biasa.
* File `.env` tidak boleh diupload ke GitHub.

---

### 6. Jalankan Aplikasi

```bash
python app.py
```

Buka browser:

```text
http://127.0.0.1:5000
```

---

## Cara Penggunaan

### 1. Register

Buka halaman register, lalu buat akun baru menggunakan email aktif.

---

### 2. Login

Login menggunakan username dan password yang sudah dibuat.

---

### 3. Verifikasi OTP

Masukkan kode OTP yang dikirim ke email.

---

### 4. Upload File TCP

Masuk ke menu **Upload File TCP**, pilih file, lalu klik upload.

File akan dikirim menggunakan TCP dan disimpan di server.

---

### 5. Streaming Video UDP

Masuk ke menu **Streaming Video UDP**, upload video, lalu klik **Putar Video**.

Video akan diproses frame-by-frame dan dikirim menggunakan UDP.

---

## Mekanisme Client-Server

Aplikasi ini menerapkan beberapa bentuk komunikasi client-server:

### Browser Client ke Flask Server

Browser mengirim request ke Flask menggunakan HTTP.

Contoh:

* Login
* Register
* Upload file
* Upload video
* Membuka dashboard

---

### Flask sebagai TCP Client ke TCP Server

Saat user mengupload file, Flask bertindak sebagai client yang mengirim file ke TCP Server.

TCP Server menerima file dan menyimpannya pada folder `tcp/received_files/`.

---

### UDP Sender ke UDP Receiver

Saat video diputar, UDP Sender membaca video frame-by-frame dan mengirimkan frame ke UDP Receiver.

UDP Receiver menerima frame dan Flask menampilkannya ke halaman website.

---

## Error Handling

Aplikasi menangani beberapa kemungkinan error, seperti:

* Username atau password salah
* OTP salah
* Email gagal dikirim
* File belum dipilih
* Video belum dipilih
* Format video tidak didukung
* TCP Server gagal menerima file
* Video tidak ditemukan
* Database gagal terhubung

Error akan ditampilkan melalui pesan pada halaman web.

---

## Kelebihan Aplikasi

* Menggunakan lebih dari satu protokol jaringan: HTTP, TCP, dan UDP.
* Sudah berbasis web sehingga mudah digunakan.
* Memiliki sistem login dan verifikasi OTP.
* Metadata file dan video disimpan ke database MySQL.
* File dan video dapat dikelola dengan fitur CRUD.
* Tampilan antarmuka dibuat modern dan responsif.
* Cocok untuk demonstrasi konsep client-server.

---

## Kekurangan Aplikasi

* UDP streaming hanya mengirim frame video tanpa audio.
* Aplikasi masih berjalan pada server lokal.
* Belum menggunakan HTTPS.
* Belum ada sistem role admin dan user.
* Belum ada pembatasan ukuran upload yang kompleks.
* Belum menggunakan cloud storage untuk menyimpan file besar.

---

## Pengembangan Selanjutnya

Beberapa pengembangan yang dapat dilakukan:

* Menambahkan HTTPS agar komunikasi lebih aman.
* Menambahkan autentikasi berbasis role.
* Menambahkan validasi ukuran dan tipe file yang lebih ketat.
* Menggunakan cloud storage untuk menyimpan file dan video.
* Menambahkan audio streaming pada fitur UDP.
* Menambahkan sistem monitoring koneksi client-server.
* Menambahkan deployment ke server publik menggunakan Cloudflare DNS.
* Menggunakan database production seperti MySQL Server pada VPS.

---

## Kesimpulan

Network App merupakan aplikasi pemrograman jaringan berbasis web yang menerapkan konsep client-server dengan menggunakan protokol HTTP, TCP, dan UDP.

TCP digunakan untuk transfer file karena membutuhkan pengiriman data yang reliable, utuh, dan berurutan. UDP digunakan untuk streaming video karena lebih cepat dan cocok untuk pengiriman data real-time. HTTP digunakan sebagai komunikasi antara browser dan server Flask.

Dengan aplikasi ini, konsep dasar pemrograman jaringan seperti socket programming, client-server, pengiriman data, penerimaan data, database, dan error handling dapat diimplementasikan secara nyata dalam satu sistem aplikasi.

---

## Author

Nama: Muhammad Ferdi
Mata Kuliah: Pemrograman Jaringan
Kelas : 4IA07
NPM   : 51422055
Project: Network App — TCP File Transfer & UDP Video Streaming

````

