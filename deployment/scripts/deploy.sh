#!/bin/bash

# BYF Mühendislik - Deployment Script

set -e

echo "🚀 BYF Mühendislik Deployment Başlatılıyor..."

# Environment kontrolü
if [ -z "$1" ]; then
    echo "❌ Environment belirtilmedi: ./deploy.sh [production|staging]"
    exit 1
fi

ENVIRONMENT=$1
cd /opt/byf_muhendislik

echo "📦 Environment: $ENVIRONMENT"

# Maintenance modu aç
echo "🛠️  Maintenance modu açılıyor..."
docker-compose exec web python manage.py maintenance on

# Kod güncelleme
echo "📥 Kod güncelleniyor..."
git pull origin main

# Bağımlılıklar
echo "📚 Bağımlılıklar yükleniyor..."
docker-compose exec web pip install -r requirements.txt

# Database migration
echo "🗃️  Database migration'ları uygulanıyor..."
docker-compose exec web python manage.py migrate

# Static dosyalar
echo "📁 Static dosyalar toplanıyor..."
docker-compose exec web python manage.py collectstatic --noinput

# Cache temizleme
echo "🧹 Cache temizleniyor..."
docker-compose exec web python manage.py clear_cache

# Servisleri yeniden başlat
echo "🔄 Servisler yeniden başlatılıyor..."
docker-compose down
docker-compose up -d

# Health check
echo "🏥 Health check yapılıyor..."
sleep 30
curl -f http://localhost/health/ || {
    echo "❌ Health check başarısız"
    exit 1
}

# Maintenance modu kapat
echo "✅ Maintenance modu kapatılıyor..."
docker-compose exec web python manage.py maintenance off

echo "🎉 BYF Mühendislik başarıyla deploy edildi!"
echo "📊 Sistem durumu: http://localhost/health/"