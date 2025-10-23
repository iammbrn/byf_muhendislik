#!/bin/bash

set -e

check_service() {
    systemctl is-active --quiet "$1" && echo "✅ $1" || echo "❌ $1"
}

check_service byf_gunicorn
check_service nginx
check_service postgresql
check_service redis-server

HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" http://localhost/)
[ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] && echo "✅ Web ($HTTP_CODE)" || echo "❌ Web ($HTTP_CODE)"

