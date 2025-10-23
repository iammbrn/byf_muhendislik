#!/bin/bash

################################################################################
# BYF Mühendislik - Production Deployment Script
# Git repository'den kod çekip production'a deploy eder
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/opt/byf_muhendislik"
BACKEND_DIR="$PROJECT_DIR/backend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 BYF Mühendislik Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalı${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Git branch kontrol
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "\n${BLUE}📌 Mevcut branch: $CURRENT_BRANCH${NC}"

read -p "Deploy edilecek branch (varsayılan: main): " DEPLOY_BRANCH
DEPLOY_BRANCH=${DEPLOY_BRANCH:-main}

# Backup al
echo -e "\n${BLUE}💾 Deployment öncesi backup alınıyor...${NC}"
bash /opt/byf_muhendislik/deployment/scripts/backup_production.sh

# Maintenance mode aç (opsiyonel - özel bir view gerekir)
echo -e "\n${BLUE}🛠️  Maintenance modu...${NC}"

# Git pull
echo -e "\n${BLUE}📥 Kod güncelleniyor (branch: $DEPLOY_BRANCH)...${NC}"
git fetch origin
git checkout "$DEPLOY_BRANCH"
git pull origin "$DEPLOY_BRANCH"

COMMIT_HASH=$(git rev-parse --short HEAD)
echo -e "${GREEN}✅ Commit: $COMMIT_HASH${NC}"

# Virtual environment aktivasyonu
source "$PROJECT_DIR/venv/bin/activate"

# Dependencies güncelle
echo -e "\n${BLUE}📚 Python bağımlılıkları güncelleniyor...${NC}"
cd "$BACKEND_DIR"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Bağımlılıklar güncellendi${NC}"

# Database migration
echo -e "\n${BLUE}🗃️  Database migration'ları kontrol ediliyor...${NC}"
python manage.py migrate --check || {
    echo -e "${YELLOW}⚠️  Uygulanmamış migration'lar var${NC}"
    python manage.py showmigrations --plan
    read -p "Migration'ları uygula? (y/n): " APPLY_MIGRATIONS
    
    if [ "$APPLY_MIGRATIONS" = "y" ]; then
        python manage.py migrate --noinput
        echo -e "${GREEN}✅ Migration'lar uygulandı${NC}"
    fi
}

# Static files topla
echo -e "\n${BLUE}📁 Static dosyalar toplanıyor...${NC}"
python manage.py collectstatic --noinput --clear
echo -e "${GREEN}✅ Static dosyalar toplandı${NC}"

# Permission'ları düzelt
echo -e "\n${BLUE}🔐 Dosya izinleri düzenleniyor...${NC}"
chown -R www-data:www-data "$BACKEND_DIR/media"
chown -R www-data:www-data "$BACKEND_DIR/staticfiles"
chmod -R 755 "$BACKEND_DIR/media"
chmod -R 755 "$BACKEND_DIR/staticfiles"

# Gunicorn'u yeniden başlat
echo -e "\n${BLUE}🔄 Gunicorn yeniden başlatılıyor...${NC}"
systemctl restart byf_gunicorn

# Gunicorn durumunu kontrol et
sleep 3
if systemctl is-active --quiet byf_gunicorn; then
    echo -e "${GREEN}✅ Gunicorn başarıyla yeniden başlatıldı${NC}"
else
    echo -e "${RED}❌ Gunicorn başlatılamadı! Log kontrol ediliyor...${NC}"
    journalctl -u byf_gunicorn -n 50 --no-pager
    exit 1
fi

# Nginx reload
echo -e "\n${BLUE}🔄 Nginx reload...${NC}"
nginx -t && systemctl reload nginx

# Health check
echo -e "\n${BLUE}🏥 Health check yapılıyor...${NC}"
sleep 5

DOMAIN=$(grep ALLOWED_HOSTS "$BACKEND_DIR/.env" | cut -d'=' -f2 | cut -d',' -f1)
if [ -z "$DOMAIN" ]; then
    DOMAIN="localhost"
fi

HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "http://localhost/")
if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 301 ] || [ "$HTTP_CODE" -eq 302 ]; then
    echo -e "${GREEN}✅ Health check başarılı (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Health check başarısız (HTTP $HTTP_CODE)${NC}"
    echo -e "${YELLOW}Nginx error log kontrol ediliyor...${NC}"
    tail -n 20 /var/log/nginx/byf_error.log
    exit 1
fi

# Deployment log
echo -e "\n${BLUE}📝 Deployment log kaydediliyor...${NC}"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deployed: $DEPLOY_BRANCH @ $COMMIT_HASH" >> /var/log/byf_deployments.log

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment başarıyla tamamlandı!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Özeti:${NC}"
echo -e "   Branch: $DEPLOY_BRANCH"
echo -e "   Commit: $COMMIT_HASH"
echo -e "   Tarih: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "   Domain: $DOMAIN"
echo ""
echo -e "${BLUE}🔍 Kontrol:${NC}"
echo -e "   ${GREEN}systemctl status byf_gunicorn${NC}"
echo -e "   ${GREEN}tail -f /var/log/byf/gunicorn-error.log${NC}"
echo -e "   ${GREEN}tail -f /var/log/nginx/byf_error.log${NC}"


