#!/bin/bash

################################################################################
# BYF Mühendislik - Backup Restore Script
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKUP_DIR="/opt/backups/byf_muhendislik"

echo -e "${BLUE}📦 BYF Mühendislik Backup Restore${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalı${NC}"
    exit 1
fi

# Backup listesini göster
echo -e "\n${BLUE}📋 Mevcut Database Backup'ları:${NC}"
ls -lht "$BACKUP_DIR/database"/*.sql.gz | head -20

echo ""
read -p "Restore edilecek backup dosyasının tam yolu: " BACKUP_FILE

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup dosyası bulunamadı: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "\n${RED}⚠️  UYARI: Bu işlem mevcut veritabanını silecek!${NC}"
read -p "Devam etmek istediğinizden emin misiniz? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "İşlem iptal edildi"
    exit 0
fi

# Gunicorn'u durdur
echo -e "\n${BLUE}🛑 Gunicorn durduruluyor...${NC}"
systemctl stop byf_gunicorn

# Database'i restore et
echo -e "\n${BLUE}🗃️  Database restore ediliyor...${NC}"

# Mevcut database'i drop ve yeniden oluştur
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS byf_muhendislik;
CREATE DATABASE byf_muhendislik;
GRANT ALL PRIVILEGES ON DATABASE byf_muhendislik TO byf_user;
\q
EOF

# Backup'ı restore et
gunzip -c "$BACKUP_FILE" | sudo -u postgres psql byf_muhendislik

echo -e "${GREEN}✅ Database restore edildi${NC}"

# Media backup restore (opsiyonel)
read -p "Media dosyalarını da restore etmek istiyor musunuz? (y/n): " RESTORE_MEDIA

if [ "$RESTORE_MEDIA" = "y" ]; then
    echo -e "\n${BLUE}📋 Mevcut Media Backup'ları:${NC}"
    ls -lht "$BACKUP_DIR/media"/*.tar.gz | head -20
    
    echo ""
    read -p "Restore edilecek media backup dosyasının tam yolu: " MEDIA_BACKUP_FILE
    
    if [ -f "$MEDIA_BACKUP_FILE" ]; then
        echo -e "\n${BLUE}📁 Media dosyaları restore ediliyor...${NC}"
        tar -xzf "$MEDIA_BACKUP_FILE" -C /opt/byf_muhendislik/backend/
        echo -e "${GREEN}✅ Media dosyaları restore edildi${NC}"
    else
        echo -e "${YELLOW}⚠️  Media backup dosyası bulunamadı${NC}"
    fi
fi

# Migration'ları çalıştır
echo -e "\n${BLUE}🔄 Django migration'ları çalıştırılıyor...${NC}"
cd /opt/byf_muhendislik/backend
source ../venv/bin/activate
python manage.py migrate --noinput

# Gunicorn'u başlat
echo -e "\n${BLUE}🚀 Gunicorn başlatılıyor...${NC}"
systemctl start byf_gunicorn
systemctl status byf_gunicorn --no-pager

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Restore işlemi tamamlandı!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${BLUE}🔍 Siteyi kontrol edin:${NC}"
echo -e "   Tarayıcınızdan sitenizi açın"


