#!/bin/bash

################################################################################
# BYF Mühendislik - Production Backup Script
# Günlük otomatik backup için cron job ile kullanılabilir
################################################################################

set -e

# Yapılandırma
BACKUP_DIR="/opt/backups/byf_muhendislik"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}💾 BYF Mühendislik Backup Başlatılıyor...${NC}"
echo "Tarih: $(date '+%Y-%m-%d %H:%M:%S')"

# Backup dizinini oluştur
mkdir -p "$BACKUP_DIR"/{database,media}

# 1. PostgreSQL Database Backup
echo -e "\n${BLUE}🗃️  PostgreSQL veritabanı yedekleniyor...${NC}"
DB_BACKUP_FILE="$BACKUP_DIR/database/db_backup_$DATE.sql"

sudo -u postgres pg_dump byf_muhendislik > "$DB_BACKUP_FILE"
gzip "$DB_BACKUP_FILE"

DB_SIZE=$(du -h "${DB_BACKUP_FILE}.gz" | cut -f1)
echo -e "${GREEN}✅ Database backup tamamlandı: ${DB_BACKUP_FILE}.gz ($DB_SIZE)${NC}"

# 2. Media Files Backup
echo -e "\n${BLUE}📁 Media dosyaları yedekleniyor...${NC}"
MEDIA_BACKUP_FILE="$BACKUP_DIR/media/media_backup_$DATE.tar.gz"

if [ -d "/opt/byf_muhendislik/backend/media" ]; then
    tar -czf "$MEDIA_BACKUP_FILE" -C /opt/byf_muhendislik/backend media/
    MEDIA_SIZE=$(du -h "$MEDIA_BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Media backup tamamlandı: $MEDIA_BACKUP_FILE ($MEDIA_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠️  Media dizini bulunamadı${NC}"
fi

# 3. Eski backup'ları temizle
echo -e "\n${BLUE}🧹 Eski backup'lar temizleniyor (${RETENTION_DAYS} günden eski)...${NC}"
DELETED_DB=$(find "$BACKUP_DIR/database" -name "*.gz" -type f -mtime +${RETENTION_DAYS} | wc -l)
find "$BACKUP_DIR/database" -name "*.gz" -type f -mtime +${RETENTION_DAYS} -delete
DELETED_MEDIA=$(find "$BACKUP_DIR/media" -name "*.tar.gz" -type f -mtime +${RETENTION_DAYS} | wc -l)
find "$BACKUP_DIR/media" -name "*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
echo -e "${GREEN}✅ Silinen backup sayısı: DB=$DELETED_DB, Media=$DELETED_MEDIA${NC}"

# 4. Backup özeti
echo -e "\n${BLUE}📊 Backup Özeti:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Toplam DB Backup: $(find "$BACKUP_DIR/database" -name "*.gz" | wc -l) adet"
echo "Toplam Media Backup: $(find "$BACKUP_DIR/media" -name "*.tar.gz" | wc -l) adet"
echo "Toplam Backup Boyutu: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo "Son DB Backup: ${DB_BACKUP_FILE}.gz ($DB_SIZE)"
[ -f "$MEDIA_BACKUP_FILE" ] && echo "Son Media Backup: $MEDIA_BACKUP_FILE ($MEDIA_SIZE)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "\n${GREEN}✅ Backup işlemi başarıyla tamamlandı!${NC}"

# Backup log'a kaydet
echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup completed: DB=$DB_SIZE" >> /var/log/byf_backup.log


