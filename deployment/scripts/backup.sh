#!/bin/bash

# BYF Mühendislik - Backup Script

set -e

BACKUP_DIR="/opt/backups/byf_muhendislik"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

echo "💾 BYF Mühendislik Backup Başlatılıyor..."

# Backup dizinini oluştur
mkdir -p $BACKUP_DIR

# Database backup
echo "🗃️  Database yedekleniyor..."
docker-compose exec db pg_dump -U byf_user byf_muhendislik > $BACKUP_FILE

# Backup'ı sıkıştır
echo "📦 Backup sıkıştırılıyor..."
gzip $BACKUP_FILE

# Eski backup'ları temizle (30 günden eski)
echo "🧹 Eski backup'lar temizleniyor..."
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup tamamlandı: ${BACKUP_FILE}.gz"