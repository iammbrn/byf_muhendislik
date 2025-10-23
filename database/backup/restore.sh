#!/bin/bash

# BYF Mühendislik Veritabanı Geri Yükleme Scripti

set -e

# Config
BACKUP_FILE=$1
DB_NAME="byf_muhendislik"
DB_USER="byf_user"
DB_HOST="localhost"
DB_PORT="5432"
LOG_FILE="/var/log/byf_restore.log"

# Log fonksiyonu
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Hata yönetimi
error_exit() {
    log "HATA: $1"
    exit 1
}

# Parametre kontrolü
if [ -z "$BACKUP_FILE" ]; then
    echo "Kullanım: $0 <yedek_dosyası.dump>"
    echo "Mevcut yedekler:"
    ls -la /opt/byf_muhendislik/backups/*.dump 2>/dev/null || echo "Yedek dosyası bulunamadı"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    error_exit "Yedek dosyası bulunamadı: $BACKUP_FILE"
fi

# Onay
read -p "$BACKUP_FILE dosyasından geri yükleme yapılacak. Emin misiniz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "İşlem iptal edildi."
    exit 1
fi

log "Geri yükleme başlatılıyor: $BACKUP_FILE"

# Mevcut bağlantıları sonlandır
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres \
    -c "SELECT pg_terminate_backend(pg_stat_activity.pid) 
        FROM pg_stat_activity 
        WHERE pg_stat_activity.datname = '$DB_NAME' 
        AND pid <> pg_backend_pid();" 2>/dev/null || true

# Veritabanını drop et ve yeniden oluştur
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres \
    -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>> $LOG_FILE
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres \
    -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER ENCODING 'UTF8';" 2>> $LOG_FILE

# Geri yükleme işlemi
pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --verbose \
    --no-password \
    --clean \
    --if-exists \
    "$BACKUP_FILE" 2>> $LOG_FILE

if [ $? -eq 0 ]; then
    log "Geri yükleme başarılı: $BACKUP_FILE"
    
    # İstatistikleri güncelle
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
        -c "ANALYZE;" 2>> $LOG_FILE
    log "Veritabanı istatistikleri güncellendi"
else
    error_exit "Geri yükleme sırasında hata oluştu"
fi

log "Geri yükleme işlemi tamamlandı"
echo "Geri yükleme başarıyla tamamlandı: $BACKUP_FILE"