# Production Deployment Guide

This guide outlines the steps to deploy the **DishaPath** application to a production Linux server (e.g., Ubuntu 22.04).

## Prerequisites
- **Server**: A VPS (AWS EC2, DigitalOcean Droplet, etc.) with Ubuntu 22.04.
- **Domain**: A domain name pointing to your server's IP.
- **Services**: Nginx, PostgreSQL, Gunicorn, Supervisor (or Systemd).

## 1. Server Setup

Update system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

Install required packages:
```bash
sudo apt install python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl git -y
```

Install Node.js (for Tailwind CSS):
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. Database Setup (PostgreSQL)

Create database and user:
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE careerhub;
CREATE USER careerhubuser WITH PASSWORD 'your_secure_password';
ALTER ROLE careerhubuser SET client_encoding TO 'utf8';
ALTER ROLE careerhubuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE careerhubuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE careerhub TO careerhubuser;
\q
```

## 3. Project Setup

Clone the repository:
```bash
cd /var/www
sudo git clone https://github.com/Recjvenik/careerhub.git
sudo chown -R $USER:$USER careerhub
cd careerhub
```

Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

## 4. Environment Configuration

Create `.env` file:
```bash
nano .env
```

Add the following (update with your values):
```env
DEBUG=False
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,server_ip
DATABASE_URL=postgres://careerhubuser:your_secure_password@localhost:5432/careerhub
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_SECRET=your_google_secret
```

## 5. Frontend Build

Install Node dependencies and build Tailwind CSS:
```bash
npm install
npm run build
```

## 6. Django Setup

Run migrations:
```bash
python manage.py migrate
```

Collect static files:
```bash
python manage.py collectstatic --noinput
```

Create superuser:
```bash
python manage.py createsuperuser
```

## 7. Gunicorn Setup

Test Gunicorn:
```bash
gunicorn --bind 0.0.0.0:8000 career_upskill.wsgi
```
(Press Ctrl+C to stop)

Create Systemd service file:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Content:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/careerhub
ExecStart=/var/www/careerhub/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/careerhub/careerhub.sock career_upskill.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 8. Nginx Setup

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/careerhub
```

Content:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/careerhub;
    }

    location /media/ {
        root /var/www/careerhub;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/careerhub/careerhub.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/careerhub /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 9. SSL Certificate (HTTPS)

Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

Obtain certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 10. Maintenance

- **Updates**: Pull changes, run `pip install`, `npm run build`, `migrate`, `collectstatic`, and restart Gunicorn.
- **Logs**: Check `sudo journalctl -u gunicorn` or Nginx logs in `/var/log/nginx/`.
