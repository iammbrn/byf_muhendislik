#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 404 Hatası Analiz ve Düzeltme${NC}"
echo ""

# 1. Gunicorn durumu
echo -e "${BLUE}1. Gunicorn kontrol${NC}"
systemctl status byf_gunicorn --no-pager | head -5
echo ""

# 2. Gunicorn socket var mı?
echo -e "${BLUE}2. Gunicorn socket kontrol${NC}"
if [ -S "/opt/byf_muhendislik/gunicorn.sock" ]; then
    echo -e "${GREEN}✅ Socket mevcut${NC}"
    ls -la /opt/byf_muhendislik/gunicorn.sock
else
    echo -e "${RED}❌ Socket yok!${NC}"
    echo "Gunicorn restart ediliyor..."
    systemctl restart byf_gunicorn
    sleep 3
    ls -la /opt/byf_muhendislik/gunicorn.sock
fi
echo ""

# 3. Nginx config test
echo -e "${BLUE}3. Nginx config test${NC}"
nginx -t
echo ""

# 4. Nginx error log
echo -e "${BLUE}4. Son Nginx hataları${NC}"
tail -n 20 /var/log/nginx/byf_error.log
echo ""

# 5. Gunicorn log
echo -e "${BLUE}5. Son Gunicorn logları${NC}"
tail -n 20 /var/log/byf/gunicorn-error.log
echo ""

# 6. Test request
echo -e "${BLUE}6. Test request${NC}"
curl -v http://localhost/ 2>&1 | head -20
echo ""

echo -e "${BLUE}Olası Çözümler:${NC}"
echo "1. systemctl restart byf_gunicorn"
echo "2. systemctl reload nginx"
echo "3. journalctl -u byf_gunicorn -n 50"

