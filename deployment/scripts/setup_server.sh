#!/bin/bash

################################################################################
# BYF Mühendislik - VPS Sunucu Kurulum Scripti
# KVM1 (4GB RAM, 1 vCPU, 50GB Disk) için optimize edilmiştir
# Ubuntu 22.04 LTS için hazırlanmıştır
################################################################################

set -e

# Renkli output için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BYF Mühendislik VPS Kurulum${NC}"
echo -e "${BLUE}========================================${NC}"

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalı${NC}"
    echo "Kullanım: sudo bash setup_server.sh"
    exit 1
fi

# Domain adı al
read -p "🌐 Domain adınız (örn: byfmuhendislik.com): " DOMAIN_NAME
read -p "📧 Admin email adresi (SSL sertifikası için): " ADMIN_EMAIL
read -p "🔐 PostgreSQL database password: " -s DB_PASSWORD
echo ""
read -p "🔑 Django SECRET_KEY (boş bırakılırsa otomatik oluşturulur): " DJANGO_SECRET
echo ""

# Secret key oluştur (Django olmadan)
if [ -z "$DJANGO_SECRET" ]; then
    DJANGO_SECRET=$(openssl rand -base64 48 | tr -d '/+=' | cut -c1-50)
    echo -e "${GREEN}✅ Django SECRET_KEY otomatik oluşturuldu${NC}"
fi

echo -e "\n${BLUE}📦 1/10: Sistem güncelleniyor...${NC}"
apt-get update
apt-get upgrade -y

echo -e "\n${BLUE}📦 2/10: Gerekli paketler yükleniyor...${NC}"
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    nginx \
    git \
    ufw \
    certbot \
    python3-certbot-nginx \
    redis-server \
    curl \
    wget \
    htop \
    fail2ban \
    build-essential

echo -e "\n${BLUE}🗃️  3/10: PostgreSQL yapılandırılıyor...${NC}"
sudo -u postgres psql <<EOF
CREATE DATABASE byf_muhendislik;
CREATE USER byf_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE byf_user SET client_encoding TO 'utf8';
ALTER ROLE byf_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE byf_user SET timezone TO 'Europe/Istanbul';
GRANT ALL PRIVILEGES ON DATABASE byf_muhendislik TO byf_user;
\c byf_muhendislik
GRANT ALL ON SCHEMA public TO byf_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO byf_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO byf_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO byf_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO byf_user;
\q
EOF

echo -e "${GREEN}✅ PostgreSQL veritabanı oluşturuldu${NC}"

echo -e "\n${BLUE}🔴 4/10: Redis yapılandırılıyor...${NC}"
systemctl enable redis-server
systemctl start redis-server
echo -e "${GREEN}✅ Redis başlatıldı${NC}"

echo -e "\n${BLUE}📁 5/10: Uygulama dizini oluşturuluyor...${NC}"
mkdir -p /opt/byf_muhendislik
cd /opt/byf_muhendislik

# Git kullanıcısını ayarla (deployment için)
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}ℹ️  Git repository'sini manuel olarak clone etmelisiniz:${NC}"
    echo -e "${YELLOW}   git clone YOUR_REPO_URL /opt/byf_muhendislik${NC}"
else
    echo -e "${GREEN}✅ Git repository zaten mevcut${NC}"
fi

echo -e "\n${BLUE}🐍 6/10: Python sanal ortamı oluşturuluyor...${NC}"
python3 -m venv venv
source venv/bin/activate

# requirements.txt kontrol et
if [ -f "backend/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    echo -e "${GREEN}✅ Python paketleri yüklendi${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt bulunamadı, manuel yükleme gerekiyor${NC}"
fi

echo -e "\n${BLUE}🔧 7/10: Environment dosyası oluşturuluyor...${NC}"

# VPS IP adresini al
VPS_IP=$(curl -s ifconfig.me)
if [ -z "$VPS_IP" ]; then
    echo -e "${YELLOW}⚠️  IP adresi alınamadı, localhost kullanılacak${NC}"
    VPS_IP="127.0.0.1"
else
    echo -e "${GREEN}✅ VPS IP: $VPS_IP${NC}"
fi

cat > /opt/byf_muhendislik/backend/.env <<EOF
SECRET_KEY=$DJANGO_SECRET
DEBUG=False
ALLOWED_HOSTS=$DOMAIN_NAME,www.$DOMAIN_NAME,$VPS_IP
CSRF_TRUSTED_ORIGINS=https://$DOMAIN_NAME,https://www.$DOMAIN_NAME
CORS_ALLOWED_ORIGINS=https://$DOMAIN_NAME,https://www.$DOMAIN_NAME
SITE_URL=https://$DOMAIN_NAME

DB_NAME=byf_muhendislik
DB_USER=byf_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=info@$DOMAIN_NAME
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=info@$DOMAIN_NAME

PASSWORD_MIN_LENGTH=12
SESSION_COOKIE_AGE=1209600
USE_S3=False
EOF

chmod 600 /opt/byf_muhendislik/backend/.env
echo -e "${GREEN}✅ Environment dosyası oluşturuldu${NC}"

echo -e "\n${BLUE}🗃️  8/10: Django migration ve static dosyalar...${NC}"
cd /opt/byf_muhendislik/backend
if [ -f "manage.py" ]; then
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    echo -e "${GREEN}✅ Django kurulumu tamamlandı${NC}"
else
    echo -e "${YELLOW}⚠️  manage.py bulunamadı, manuel migration gerekiyor${NC}"
fi

echo -e "\n${BLUE}🔧 9/10: Gunicorn ve Nginx yapılandırılıyor...${NC}"

mkdir -p /var/log/byf
chown www-data:www-data /var/log/byf

cat > /etc/systemd/system/byf_gunicorn.service <<EOF
[Unit]
Description=BYF Muhendislik Gunicorn daemon
After=network.target postgresql.service

[Service]
Type=notify
User=root
Group=www-data
WorkingDirectory=/opt/byf_muhendislik/backend
Environment="PATH=/opt/byf_muhendislik/venv/bin"
ExecStart=/opt/byf_muhendislik/venv/bin/gunicorn \\
    --workers 3 \\
    --worker-class sync \\
    --bind unix:/opt/byf_muhendislik/gunicorn.sock \\
    --access-logfile /var/log/byf/gunicorn-access.log \\
    --error-logfile /var/log/byf/gunicorn-error.log \\
    --timeout 60 \\
    --max-requests 1000 \\
    --max-requests-jitter 50 \\
    byf_muhendislik.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Nginx yapılandırması (HTTP only - SSL sonra eklenecek)
cat > /etc/nginx/sites-available/byf_muhendislik <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    client_max_body_size 50M;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location /static/ {
        alias /opt/byf_muhendislik/backend/staticfiles/;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/byf_muhendislik/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://unix:/opt/byf_muhendislik/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss image/svg+xml;
}
EOF

# Nginx site'ı aktifleştir
ln -sf /etc/nginx/sites-available/byf_muhendislik /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Nginx test
nginx -t

echo -e "\n${BLUE}🔒 10/10: Firewall yapılandırılıyor...${NC}"
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw status

echo -e "\n${BLUE}🚀 Servisler başlatılıyor...${NC}"
systemctl daemon-reload
systemctl enable byf_gunicorn
systemctl start byf_gunicorn
systemctl restart nginx

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Sunucu kurulumu tamamlandı!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Sonraki Adımlar:${NC}"
echo ""
echo -e "1. Email şifresi ekle:"
echo -e "   ${GREEN}nano /opt/byf_muhendislik/backend/.env${NC}"
echo -e "   EMAIL_HOST_PASSWORD değiştir"
echo -e "   ${GREEN}systemctl restart byf_gunicorn${NC}"
echo ""
echo -e "2. SSL kur (DNS hazırsa):"
echo -e "   ${GREEN}bash /opt/byf_muhendislik/deployment/scripts/ssl_setup.sh${NC}"
echo ""
echo -e "3. Admin oluştur:"
echo -e "   ${GREEN}cd /opt/byf_muhendislik/backend${NC}"
echo -e "   ${GREEN}source ../venv/bin/activate${NC}"
echo -e "   ${GREEN}python manage.py createsuperuser${NC}"
echo ""
echo -e "Kontrol: ${GREEN}bash /opt/byf_muhendislik/deployment/scripts/monitoring.sh${NC}"


