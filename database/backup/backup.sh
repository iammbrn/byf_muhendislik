#!/bin/bash

# BYF Mühendislik Veritabanı Yedekleme Scripti
# PostgreSQL veritabanı yedekleme ve yönetimi

set -e

# Config
BACKUP_DIR="/opt/byf_muhendislik/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/byf_muhendislik_$DATE.sql"
LOG_FILE="/var/log/byf_backup.log"
RETENTION_DAYS=30

# PostgreSQL bağlantı bilgileri
DB_NAME="byf_muhendislik"
DB_USER="byf_user"
DB_HOST="localhost"
DB_PORT="5432"

# Log fonksiyonu
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Hata yönetimi
error_exit() {
    log "HATA: $1"
    exit 1
}

# Backup dizinini kontrol et
mkdir -p $BACKUP_DIR || error_exit "Backup dizini oluşturulamadı: $BACKUP_DIR"

log "Yedekleme başlatılıyor: $BACKUP_FILE"

# Yedekleme işlemi
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --verbose \
    --no-password \
    --format=custom \
    --compress=9 \
    --file="${BACKUP_FILE}.dump" 2>> $LOG_FILE

if [ $? -eq 0 ]; then
    log "Yedekleme başarılı: ${BACKUP_FILE}.dump"
    
    # Boyut kontrolü
    FILE_SIZE=$(du -h "${BACKUP_FILE}.dump" | cut -f1)
    log "Yedek dosya boyutu: $FILE_SIZE"
else
    error_exit "Yedekleme sırasında hata oluştu"
fi

# Eski yedekleri temizleme
log "$RETENTION_DAYS günden eski yedekler temizleniyor..."
find $BACKUP_DIR -name "byf_muhendislik_*.dump" -mtime +$RETENTION_DAYS -delete >> $LOG_FILE 2>&1

# Disk kullanımı bilgisi
DISK_USAGE=$(df -h $BACKUP_DIR | tail -1)
log "Disk kullanımı: $DISK_USAGE"

log "Yedekleme işlemi tamamlandı"