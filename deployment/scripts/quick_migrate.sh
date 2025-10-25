#!/bin/bash
# Quick migration deployment for service card image feature

set -e

PROJECT_DIR="/opt/byf_muhendislik"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "🔄 Applying service card image migration..."

cd "$PROJECT_DIR"
source venv/bin/activate
cd "$BACKEND_DIR"

# Run migrations
python manage.py migrate core --noinput

# Collect static
python manage.py collectstatic --noinput

# Restart gunicorn
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart byf_gunicorn

echo "✅ Migration deployed successfully!"
echo "🌐 Check: https://byfmuhendislik.com/"

