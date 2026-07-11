# 🚀 AWS EC2 Deployment Guide — Har Ghar Solar

Complete step-by-step guide to deploy on **AWS EC2 + Ubuntu 22.04 + Gunicorn + Nginx + Systemd**.

---

## 1. Launch EC2 Instance

1. Open AWS Console → EC2 → **Launch Instance**
2. **AMI**: Ubuntu Server 22.04 LTS (64-bit x86)
3. **Instance type**: t3.small (minimum) or t3.medium (recommended)
4. **Key pair**: Create or select an existing `.pem` key
5. **Security Group** — inbound rules:

   | Type | Port | Source |
   |---|---|---|
   | SSH | 22 | Your IP only |
   | HTTP | 80 | 0.0.0.0/0 |
   | HTTPS | 443 | 0.0.0.0/0 |

6. **Storage**: 20 GB gp3 (minimum)
7. Launch and note the **Public IP**

---

## 2. Connect to EC2

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## 3. System Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git
```

---

## 4. Clone & Configure the Project

```bash
cd /home/ubuntu
git clone https://github.com/YOUR_ORG/har-ghar-solar.git
cd har-ghar-solar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
nano .env
```

Edit `.env`:
```
SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=sqlite:///solar.db
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAIL=admin@hargharsolar.in
```

---

## 5. Test Gunicorn

```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 app:app
# Visit http://YOUR_EC2_PUBLIC_IP:5000 to verify
# Ctrl+C to stop
```

---

## 6. Create Systemd Service

```bash
sudo nano /etc/systemd/system/hargharsolar.service
```

Paste:
```ini
[Unit]
Description=Har Ghar Solar Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/har-ghar-solar
Environment="PATH=/home/ubuntu/har-ghar-solar/venv/bin"
EnvironmentFile=/home/ubuntu/har-ghar-solar/.env
ExecStart=/home/ubuntu/har-ghar-solar/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/ubuntu/har-ghar-solar/hargharsolar.sock \
    --timeout 120 \
    --access-logfile /var/log/hargharsolar/access.log \
    --error-logfile /var/log/hargharsolar/error.log \
    app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/log/hargharsolar
sudo chown ubuntu:ubuntu /var/log/hargharsolar

sudo systemctl daemon-reload
sudo systemctl enable hargharsolar
sudo systemctl start hargharsolar
sudo systemctl status hargharsolar   # Should show: active (running)
```

---

## 7. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/hargharsolar
```

Paste (replace `YOUR_DOMAIN_OR_IP`):
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP www.YOUR_DOMAIN_OR_IP;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Static files served directly by Nginx
    location /static/ {
        alias /home/ubuntu/har-ghar-solar/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Proxy to Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/har-ghar-solar/hargharsolar.sock;
        proxy_read_timeout 120;
        proxy_connect_timeout 120;
        proxy_send_timeout 120;
        client_max_body_size 16M;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/hargharsolar /etc/nginx/sites-enabled/
sudo nginx -t          # Must output: syntax is ok + test is successful
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 8. SSL with Let's Encrypt (HTTPS)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.in -d www.yourdomain.in
# Follow prompts; certbot auto-updates Nginx config
sudo systemctl reload nginx
```

Auto-renewal (already set up by certbot, verify):
```bash
sudo certbot renew --dry-run
```

---

## 9. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 10. Useful Management Commands

```bash
# View application logs
sudo journalctl -u hargharsolar -f

# Restart after code update
cd /home/ubuntu/har-ghar-solar
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart hargharsolar

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Check app access log
sudo tail -f /var/log/hargharsolar/access.log
```

---

## 11. Post-Deployment Checklist

- [ ] Change default admin password (`admin` / `admin123`)
- [ ] Set a strong `SECRET_KEY` in `.env`
- [ ] Verify HTTPS certificate is active
- [ ] Test contact form end-to-end
- [ ] Test Excel export download
- [ ] Test vendor login
- [ ] Verify visitor counter increments
- [ ] Set up automated backups for SQLite (`instance/solar.db`)
- [ ] Configure CloudWatch or a monitoring service (optional)

---

## 12. SQLite Backup Script

```bash
sudo nano /etc/cron.daily/backup-hargharsolar
```

```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p "$BACKUP_DIR"
cp /home/ubuntu/har-ghar-solar/instance/solar.db \
   "$BACKUP_DIR/solar_$(date +%Y%m%d_%H%M%S).db"
# Keep last 30 backups
ls -t "$BACKUP_DIR"/solar_*.db | tail -n +31 | xargs -r rm
```

```bash
sudo chmod +x /etc/cron.daily/backup-hargharsolar
```

---

## Architecture Summary

```
Internet
   │
   ▼
AWS EC2 (Ubuntu 22.04)
   │
Nginx :80/:443  ──► Static files served directly
   │
   ▼ (Unix socket)
Gunicorn (3 workers)
   │
   ▼
Flask app (app.py)
   │
SQLite (instance/solar.db)
```
