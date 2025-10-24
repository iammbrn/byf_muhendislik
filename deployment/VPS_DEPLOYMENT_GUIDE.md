# 🚀 BYF Mühendislik - VPS Deployment

## Hostinger KVM1 (4GB RAM, 1 vCPU, 50GB) - Ubuntu 22.04

---

## Ön Hazırlık

### 1. VPS Satın Al
- Hostinger KVM1, Germany (Frankfurt), Ubuntu 22.04

### 2. Domain DNS Ayarları
```
A Record: @ → VPS_IP
A Record: www → VPS_IP
```

### 3. SSH Bağlan
```bash
ssh root@VPS_IP
```

---

## Kurulum

### 1. Proje Dosyalarını Yükle

```bash
mkdir -p /opt/byf_muhendislik
cd /opt/byf_muhendislik
# Git clone VEYA FileZilla ile dosyaları yükle
```

### 2. Setup Script Çalıştır

```bash
cd /opt/byf_muhendislik/deployment/scripts
chmod +x setup_server.sh
sudo bash setup_server.sh
```

**Girilecek bilgiler:**
- Domain: byfmuhendislik.com
- Email: admin@byfmuhendislik.com
- PostgreSQL şifresi: (güçlü şifre)
- Django SECRET_KEY: (Enter - otomatik oluşur)

### 3. Email Şifresi Ekle

```bash
nano /opt/byf_muhendislik/backend/.env
```

Değiştir:
```env
EMAIL_HOST_PASSWORD=HOSTINGER_EMAIL_SIFRENIZ
```

Kaydet ve restart:
```bash
systemctl restart byf_gunicorn
```

### 4. SSL Kur (DNS hazır olduktan sonra)

```bash
cd /opt/byf_muhendislik/deployment/scripts
chmod +x ssl_setup.sh
sudo bash ssl_setup.sh
```

### 5. Admin Kullanıcı Oluştur

```bash
cd /opt/byf_muhendislik/backend
source ../venv/bin/activate
python manage.py createsuperuser
```

---

## Deployment (Kod Güncelleme)

```bash
cd /opt/byf_muhendislik/deployment/scripts
sudo bash deploy_production.sh
```

---

## Backup

### Otomatik Günlük Backup
```bash
sudo crontab -e
# Ekle: 0 2 * * * /opt/byf_muhendislik/deployment/scripts/backup_production.sh
```

### Manuel Backup
```bash
sudo bash /opt/byf_muhendislik/deployment/scripts/backup_production.sh
```

### Restore
```bash
sudo bash /opt/byf_muhendislik/deployment/scripts/restore_backup.sh
```

---

## Monitoring

```bash
sudo bash monitoring.sh
```

---

## Servis Yönetimi

```bash
# Gunicorn
systemctl restart byf_gunicorn
systemctl status byf_gunicorn
journalctl -u byf_gunicorn -f

# Nginx
nginx -t && systemctl reload nginx

# PostgreSQL
systemctl status postgresql

# Redis
systemctl status redis-server
```

---

## Test

- Site: https://byfmuhendislik.com
- Admin: https://byfmuhendislik.com/admin/
- SSL: https://www.ssllabs.com/ssltest/

---

## Sorun Giderme

### Gunicorn başlamıyor
```bash
journalctl -u byf_gunicorn -n 50 --no-pager
```

### 502 Bad Gateway
```bash
systemctl status byf_gunicorn
ls -la /opt/byf_muhendislik/gunicorn.sock
```

### Static files yüklenmiyor
```bash
cd /opt/byf_muhendislik/backend
source ../venv/bin/activate
python manage.py collectstatic --noinput
chown -R www-data:www-data staticfiles/
```

---

## Kontrol Listesi

İlk Kurulum:
- [ ] VPS satın alındı
- [ ] Domain DNS ayarları yapıldı
- [ ] setup_server.sh çalıştırıldı
- [ ] Email şifresi eklendi
- [ ] SSL kuruldu
- [ ] Admin kullanıcısı oluşturuldu
- [ ] Backup cron job eklendi
- [ ] Site test edildi

Her Deployment:
- [ ] deploy_production.sh çalıştırıldı
- [ ] Migration'lar uygulandı
- [ ] Static files toplandı
- [ ] Gunicorn restart edildi
- [ ] Site test edildi
