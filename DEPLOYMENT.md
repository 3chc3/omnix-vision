# 🚀 Deployment Guide — OMNIX VISION

This guide covers four ways to deploy OMNIX VISION, from easiest to most
controlled:

1. Streamlit Community Cloud (free, easiest)
2. Docker (any server / VPS)
3. A generic Linux VPS (manual)
4. Local network sharing

---

## ⚠️ Before You Deploy

OMNIX VISION stores data in local JSON files under `data/`. This works great
for a single instance, but note:

- On **Streamlit Community Cloud**, the filesystem is **ephemeral** — data is
  wiped on every app restart/redeploy. Fine for demos; for persistence you'd
  need an external database (planned for v2.1).
- The **camera and hand-scan** features need access to a webcam, which only
  works when the browser and app are on the same machine (local), or via a
  device with a camera. They won't work on a headless cloud server.
- For multi-user production, add HTTPS and rate limiting at the proxy layer.

---

## 1️⃣ Streamlit Community Cloud (Recommended for Demos)

The fastest way to get a public URL — free.

### Steps

1. Push your project to a **public GitHub repository**.
2. Make sure these files are in the repo root:
   - `app.py`
   - `requirements.txt`
   - `packages.txt` (system deps: ffmpeg, libgl1)
   - `.streamlit/config.toml`
3. Go to <https://share.streamlit.io> and sign in with GitHub.
4. Click **New app**, pick your repo, branch, and set the main file to
   `app.py`.
5. (Optional) Open **Advanced settings → Secrets** and paste the contents of
   your `secrets.toml` (see `.streamlit/secrets.toml.example`).
6. Click **Deploy**. First build takes a few minutes (installing OpenCV +
   MediaPipe).

### Notes

- If the build runs out of memory, comment out `mediapipe` and
  `opencv-python` in `requirements.txt` — the camera pages will degrade
  gracefully, and everything else still works.
- `packages.txt` is what installs FFmpeg + OpenCV system libraries on the
  Streamlit Cloud build image.

---

## 2️⃣ Docker (Any Server)

A `Dockerfile` is included. This is the most portable option.

### Build and run

```bash
# Build the image
docker build -t omnix-vision .

# Run it
docker run -p 8501:8501 omnix-vision
```

Then open <http://localhost:8501>.

### Persisting data with a volume

To keep user data across container restarts, mount a volume:

```bash
docker run -p 8501:8501 \
  -v omnix_data:/app/data \
  omnix-vision
```

### With secrets

```bash
docker run -p 8501:8501 \
  -v omnix_data:/app/data \
  -v $(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro \
  omnix-vision
```

### Docker Compose (optional)

```yaml
services:
  omnix:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - omnix_data:/app/data
    restart: unless-stopped

volumes:
  omnix_data:
```

Save as `docker-compose.yml`, then `docker compose up -d`.

---

## 3️⃣ Generic Linux VPS (Manual)

For full control on Ubuntu/Debian.

### Setup

```bash
# System packages
sudo apt update
sudo apt install -y python3-venv python3-pip ffmpeg libgl1 libglib2.0-0

# Clone and enter
git clone <your-repo-url>
cd My_projrct

# Virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run (test)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Keep it running with systemd

Create `/etc/systemd/system/omnix.service`:

```ini
[Unit]
Description=OMNIX VISION Streamlit App
After=network.target

[Service]
User=youruser
WorkingDirectory=/home/youruser/My_projrct
ExecStart=/home/youruser/My_projrct/.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now omnix
sudo systemctl status omnix
```

### HTTPS with Nginx (recommended)

Put Nginx in front as a reverse proxy and use Certbot for free TLS:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
```

```bash
sudo certbot --nginx -d your-domain.com
```

---

## 4️⃣ Local Network Sharing

To let others on your Wi-Fi reach the app:

```bash
streamlit run app.py --server.address 0.0.0.0
```

Find your local IP (`ipconfig` on Windows, `ip addr` on Linux), then others
visit `http://YOUR_LOCAL_IP:8501`.

---

## 🔒 Production Checklist

Before exposing OMNIX VISION publicly:

- [ ] Set a strong `secret_key` in secrets (never use the example value).
- [ ] Serve over HTTPS (Nginx + Certbot, or the platform's built-in TLS).
- [ ] Confirm `.streamlit/secrets.toml` is in `.gitignore` and never committed.
- [ ] Set `maxUploadSize` in `config.toml` to a sane limit (default 200 MB).
- [ ] Decide on data persistence (volume for Docker, or external DB).
- [ ] Remove any test/demo accounts.
- [ ] Review the Activity Log periodically for suspicious logins.

---

## 🧪 Verifying a Deployment

After deploying, smoke-test these:

1. **Register** a new account → you get a User ID.
2. **Log in** with that ID.
3. **Switch language** to Arabic → layout flips to RTL.
4. Open **Dashboard** → charts render.
5. Open **Random Tools → Password** → generates a password.
6. Open **Backup → Export** → downloads a ZIP.

If camera/hand-scan pages show a friendly "OpenCV not available" or "no
camera" message instead of crashing, that's expected on headless servers.

---

## ❓ Troubleshooting

| Problem | Fix |
| --- | --- |
| `ImportError: libGL.so.1` | Install `libgl1` (already in `packages.txt`/Dockerfile) |
| Build OOM on Streamlit Cloud | Remove `mediapipe`/`opencv-python` from requirements |
| FFmpeg features disabled | Install FFmpeg; check it's on PATH |
| Data resets on cloud | Expected — filesystem is ephemeral; use a volume/DB |
| Camera doesn't work on server | Expected — webcam needs a local device |
| Port already in use | Change `--server.port` to a free port |

---

## 📦 Files Relevant to Deployment

| File | Purpose |
| --- | --- |
| `Dockerfile` | Container build instructions |
| `.dockerignore` | Keeps the image small |
| `packages.txt` | System packages for Streamlit Cloud |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Theme + server settings |
| `.streamlit/secrets.toml.example` | Template for secrets |

Happy deploying! 🚀
