#!/bin/bash

set -e

echo "📦 Python paketleri yükleniyor..."
cd /opt/byf_muhendislik/backend
source ../venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Bağımlılıklar yüklendi"

