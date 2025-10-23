#!/bin/bash

################################################################################
# BYF Mühendislik - Sunucu İzleme Scripti
# Sunucu sağlığını kontrol eder
################################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 BYF Mühendislik Sunucu Durumu${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Sistem Bilgileri
echo -e "${BLUE}💻 Sistem Bilgileri${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Hostname: $(hostname)"
echo "IP Adresi: $(curl -s ifconfig.me)"
echo "Uptime: $(uptime -p)"
echo "OS: $(lsb_release -d | cut -f2)"
echo ""

# 2. CPU ve RAM
echo -e "${BLUE}⚡ CPU ve RAM${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{printf "%.1f", 100 - $1}')
echo "CPU Kullanımı: ${CPU_USAGE}%"

free -h | awk 'NR==2{
    printf "RAM Kullanımı: %s / %s (%.0f%%)\n", $3, $2, $3*100/$2
}'
echo ""

# 3. Disk Kullanımı
echo -e "${BLUE}💾 Disk Kullanımı${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
df -h / | awk 'NR==2{
    printf "Root: %s / %s (%s kullanımda)\n", $3, $2, $5
}'

# Proje dizini
if [ -d "/opt/byf_muhendislik" ]; then
    PROJECT_SIZE=$(du -sh /opt/byf_muhendislik | cut -f1)
    echo "Proje Dizini: $PROJECT_SIZE"
fi

# Media dizini
if [ -d "/opt/byf_muhendislik/backend/media" ]; then
    MEDIA_SIZE=$(du -sh /opt/byf_muhendislik/backend/media | cut -f1)
    echo "Media Dosyaları: $MEDIA_SIZE"
fi

# Backup dizini
if [ -d "/opt/backups/byf_muhendislik" ]; then
    BACKUP_SIZE=$(du -sh /opt/backups/byf_muhendislik | cut -f1)
    BACKUP_COUNT=$(find /opt/backups/byf_muhendislik -name "*.gz" -o -name "*.tar.gz" | wc -l)
    echo "Backup'lar: $BACKUP_SIZE ($BACKUP_COUNT dosya)"
fi
echo ""

# 4. Servis Durumları
echo -e "${BLUE}🔧 Servis Durumları${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_service() {
    if systemctl is-active --quiet "$1"; then
        echo -e "  ✅ $2: ${GREEN}Çalışıyor${NC}"
        return 0
    else
        echo -e "  ❌ $2: ${RED}Durmuş${NC}"
        return 1
    fi
}

ALL_OK=0

check_service "byf_gunicorn" "Gunicorn" || ALL_OK=1
check_service "nginx" "Nginx" || ALL_OK=1
check_service "postgresql" "PostgreSQL" || ALL_OK=1
check_service "redis-server" "Redis" || ALL_OK=1

echo ""

# 5. Network ve Bağlantılar
echo -e "${BLUE}🌐 Network${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Web site health check
if [ -f "/opt/byf_muhendislik/backend/.env" ]; then
    DOMAIN=$(grep ALLOWED_HOSTS /opt/byf_muhendislik/backend/.env | cut -d'=' -f2 | cut -d',' -f1)
    if [ ! -z "$DOMAIN" ]; then
        HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "http://localhost/" --max-time 5)
        if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 301 ] || [ "$HTTP_CODE" -eq 302 ]; then
            echo -e "  ✅ Web Site: ${GREEN}Erişilebilir${NC} (HTTP $HTTP_CODE)"
        else
            echo -e "  ❌ Web Site: ${RED}Erişilemiyor${NC} (HTTP $HTTP_CODE)"
            ALL_OK=1
        fi
    fi
fi

# SSL sertifikası
if [ -d "/etc/letsencrypt/live" ]; then
    CERT_DIR=$(ls -t /etc/letsencrypt/live | head -1)
    if [ ! -z "$CERT_DIR" ]; then
        CERT_FILE="/etc/letsencrypt/live/$CERT_DIR/cert.pem"
        if [ -f "$CERT_FILE" ]; then
            EXPIRE_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d'=' -f2)
            EXPIRE_SECONDS=$(date -d "$EXPIRE_DATE" +%s)
            NOW_SECONDS=$(date +%s)
            DAYS_LEFT=$(( ($EXPIRE_SECONDS - $NOW_SECONDS) / 86400 ))
            
            if [ $DAYS_LEFT -gt 30 ]; then
                echo -e "  ✅ SSL Sertifikası: ${GREEN}Geçerli${NC} ($DAYS_LEFT gün kaldı)"
            elif [ $DAYS_LEFT -gt 0 ]; then
                echo -e "  ⚠️  SSL Sertifikası: ${YELLOW}Yakında Dolacak${NC} ($DAYS_LEFT gün kaldı)"
            else
                echo -e "  ❌ SSL Sertifikası: ${RED}Dolmuş${NC}"
                ALL_OK=1
            fi
        fi
    fi
fi

# Nginx connections
NGINX_CONN=$(ss -tan | grep :80 | grep ESTAB | wc -l 2>/dev/null || echo "0")
echo "  Aktif Bağlantı: $NGINX_CONN"
echo ""

# 6. Database Durumu
echo -e "${BLUE}🗃️  Database${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if systemctl is-active --quiet postgresql; then
    DB_SIZE=$(sudo -u postgres psql -d byf_muhendislik -t -c "SELECT pg_size_pretty(pg_database_size('byf_muhendislik'));" 2>/dev/null | xargs)
    if [ ! -z "$DB_SIZE" ]; then
        echo "  Database Boyutu: $DB_SIZE"
    fi
    
    # Table count
    TABLE_COUNT=$(sudo -u postgres psql -d byf_muhendislik -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | xargs)
    if [ ! -z "$TABLE_COUNT" ]; then
        echo "  Tablo Sayısı: $TABLE_COUNT"
    fi
fi
echo ""

# 7. Son Loglar
echo -e "${BLUE}📋 Son Hatalar (Gunicorn)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "/var/log/byf/gunicorn-error.log" ]; then
    ERRORS=$(tail -n 100 /var/log/byf/gunicorn-error.log | grep -i "error" | tail -n 3)
    if [ -z "$ERRORS" ]; then
        echo -e "  ${GREEN}✅ Hata yok${NC}"
    else
        echo "$ERRORS"
        ALL_OK=1
    fi
else
    echo "  Log dosyası bulunamadı"
fi
echo ""

# 8. Özet
echo -e "${BLUE}========================================${NC}"
if [ $ALL_OK -eq 0 ]; then
    echo -e "${GREEN}✅ Tüm Sistemler Normal Çalışıyor${NC}"
else
    echo -e "${RED}⚠️  Bazı Sorunlar Tespit Edildi${NC}"
    echo "Detaylı log kontrolü için:"
    echo "  journalctl -u byf_gunicorn -n 50"
    echo "  tail -f /var/log/nginx/byf_error.log"
fi
echo -e "${BLUE}========================================${NC}"

exit $ALL_OK


