# BYF Mühendislik - Deployment

## Hızlı Başlangıç

```bash
# 1. Proje dosyalarını yükle
mkdir -p /opt/byf_muhendislik
cd /opt/byf_muhendislik

# 2. Setup çalıştır
cd deployment/scripts
chmod +x setup_server.sh
sudo bash setup_server.sh

# 3. Email şifresi ekle
nano /opt/byf_muhendislik/backend/.env
# EMAIL_HOST_PASSWORD değiştir

# 4. SSL kur
chmod +x ssl_setup.sh
sudo bash ssl_setup.sh

# 5. Admin oluştur
cd /opt/byf_muhendislik/backend
source ../venv/bin/activate
python manage.py createsuperuser
```

## Scriptler

- **setup_server.sh** - İlk kurulum
- **ssl_setup.sh** - SSL sertifikası
- **deploy_production.sh** - Kod güncelleme
- **backup_production.sh** - Yedekleme
- **restore_backup.sh** - Geri yükleme
- **monitoring.sh** - Sistem durumu
- **health_check.sh** - Hızlı kontrol

## Deployment

```bash
cd /opt/byf_muhendislik/deployment/scripts
sudo bash deploy_production.sh
```

## Backup

```bash
# Cron ekle
sudo crontab -e
# 0 2 * * * /opt/byf_muhendislik/deployment/scripts/backup_production.sh
```

Detaylar: VPS_DEPLOYMENT_GUIDE.md

