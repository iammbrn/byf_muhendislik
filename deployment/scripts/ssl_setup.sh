#!/bin/bash

################################################################################
# BYF Mühendislik - SSL Sertifikası Kurulum (Let's Encrypt)
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 SSL Sertifikası Kurulumu${NC}"

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalı${NC}"
    exit 1
fi

# Domain adı al
read -p "🌐 Domain adınız (örn: byfmuhendislik.com): " DOMAIN_NAME
read -p "📧 Email adresiniz: " ADMIN_EMAIL

echo -e "\n${YELLOW}⚠️  Devam etmeden önce:${NC}"
echo -e "1. Domain DNS ayarlarının yapıldığından emin olun"
echo -e "2. A Record: $DOMAIN_NAME -> Sunucu IP"
echo -e "3. A Record: www.$DOMAIN_NAME -> Sunucu IP"
echo -e "4. DNS propagation tamamlanmalı (https://dnschecker.org)"
echo ""
read -p "DNS ayarları tamamlandı mı? (y/n): " DNS_READY

if [ "$DNS_READY" != "y" ]; then
    echo -e "${YELLOW}DNS ayarlarını tamamlayıp tekrar çalıştırın${NC}"
    exit 0
fi

echo -e "\n${BLUE}🔒 SSL sertifikası alınıyor...${NC}"

# Certbot Nginx config'i otomatik güncelleyecek
certbot --nginx \
    -d "$DOMAIN_NAME" \
    -d "www.$DOMAIN_NAME" \
    --non-interactive \
    --agree-tos \
    -m "$ADMIN_EMAIL" \
    --redirect \
    --staple-ocsp

echo -e "\n${BLUE}🔄 Otomatik yenileme test ediliyor...${NC}"
certbot renew --dry-run

systemctl enable certbot.timer 2>/dev/null || true
systemctl start certbot.timer 2>/dev/null || true

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ SSL Sertifikası başarıyla kuruldu!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Test:${NC} ${GREEN}https://$DOMAIN_NAME${NC}"


