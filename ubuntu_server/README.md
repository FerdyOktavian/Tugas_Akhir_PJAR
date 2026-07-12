# Ubuntu Network Server

Folder ini berisi TCP Server dan UDP Receiver yang dijalankan di Ubuntu Server.

## Struktur

```text
ubuntu_server/
├── server_runner.py
├── tcp/
│   ├── tcp_server.py
│   └── received_files/
└── udp/
    ├── udp_receiver.py
    └── received_frames/
```

## Menjalankan sekaligus

```bash
cd ubuntu_server
python3 server_runner.py
```

## Menjalankan terpisah

```bash
python3 tcp/tcp_server.py
python3 udp/udp_receiver.py
```

Port yang digunakan:
- TCP: 6000
- UDP: 7000
