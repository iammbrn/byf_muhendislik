# 🚀 BYF Mühendislik - Deployment Paketleri

Bu dizin, BYF Mühendislik projesini **Hostinger KVM1 VPS** sunucusuna deploy etmek için gereken tüm dosyaları içerir.

## 📁 Dizin Yapısı

```
deployment/
├── README.md                      # Bu dosya
├── VPS_DEPLOYMENT_GUIDE.md        # Detaylı deployment rehberi
├── QUICK_START.md                 # Hızlı başlangıç (5 dakika)
├── .env.example                   # Environment variables şablonu
│
├── scripts/                       # Deployment scriptleri
│   ├── setup_server.sh           # ⭐ İlk kurulum (tek seferlik)
│   ├── ssl_setup.sh              # SSL sertifikası kurulumu
│   ├── deploy_production.sh      # 🔄 Kod güncelleme ve deploy
│   ├── backup_production.sh      # 💾 Manuel backup
│   ├── restore_backup.sh         # 📦 Backup restore
│   └── monitoring.sh             # 🔍 Sunucu durumu kontrolü
│
├── nginx/
│   └── nginx.conf                # Nginx yapılandırması
│
└── docker/                        # Docker yapılandırması (opsiyonel)
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 🎯 Kullanım Senaryoları

### 1️⃣ İlk Deployment (Sıfırdan Kurulum)

**Adımlar:**
1. VPS satın al (Hostinger KVM1, Germany)
2. SSH ile bağlan
3. Projeyi `/opt/byf_muhendislik` dizinine kopyala
4. `setup_server.sh` çalıştır
5. SSL sertifikası kur
6. Admin kullanıcısı oluştur

**Detaylar:** `VPS_DEPLOYMENT_GUIDE.md`

---

### 2️⃣ Kod Güncellemesi (Deployment)

Yeni kod değişikliklerini production'a almak için:

```bash
cd /opt/byf_muhendislik/deployment/scripts
sudo bash deploy_production.sh
```

**Bu script otomatik olarak:**
- ✅ Backup alır
- ✅ Git'ten son kodu çeker
- ✅ Python bağımlılıklarını günceller
- ✅ Migration'ları uygular
- ✅ Static dosyaları toplar
- ✅ Gunicorn'u yeniden başlatır
- ✅ Health check yapar

---

### 3️⃣ Backup ve Restore

**Manuel Backup:**
```bash
sudo bash /opt/byf_muhendislik/deployment/scripts/backup_production.sh
```

**Backup'ı Geri Yükle:**
```bash
sudo bash /opt/byf_muhendislik/deployment/scripts/restore_backup.sh
```

**Otomatik Günlük Backup (Cron):**
```bash
sudo crontab -e
# Ekle: 0 2 * * * /opt/byf_muhendislik/deployment/scripts/backup_production.sh
```

---

### 4️⃣ Sunucu Durumu Kontrolü

```bash
sudo bash /opt/byf_muhendislik/deployment/scripts/monitoring.sh
```

**Gösterir:**
- CPU ve RAM kullanımı
- Disk kullanımı
- Servis durumları (Gunicorn, Nginx, PostgreSQL, Redis)
- Web site erişilebilirliği
- SSL sertifikası durumu
- Database boyutu

---

## 📋 Script Açıklamaları

### `setup_server.sh` ⭐
**Amaç:** Sıfır bir VPS'e tüm gerekli yazılımları kurar ve yapılandırır.

**Kurduğu yazılımlar:**
- Python 3.10 + pip
- PostgreSQL 14
- Nginx
- Redis
- Gunicorn
- Certbot (SSL için)
- Fail2ban (güvenlik)
- UFW Firewall

**Yaptığı yapılandırmalar:**
- PostgreSQL database oluşturur
- Gunicorn systemd service kurar
- Nginx yapılandırmasını yapar
- Firewall kurallarını ayarlar
- Environment dosyası oluşturur
- Django migration'ları çalıştırır

**Kullanım:**
```bash
sudo bash setup_server.sh
```

---

### `ssl_setup.sh`
**Amaç:** Let's Encrypt SSL sertifikası kurar.

**Gereksinimler:**
- Domain DNS ayarları yapılmış olmalı
- Nginx çalışıyor olmalı

**Kullanım:**
```bash
sudo bash ssl_setup.sh
```

---

### `deploy_production.sh` 🔄
**Amaç:** Kod güncellemelerini production'a deploy eder.

**Adımlar:**
1. Pre-deployment backup
2. Git pull
3. Dependencies update
4. Database migrations
5. Static files collection
6. Gunicorn restart
7. Health check

**Kullanım:**
```bash
sudo bash deploy_production.sh
```

---

### `backup_production.sh` 💾
**Amaç:** PostgreSQL database ve media dosyalarını yedekler.

**Yedekleme dizini:** `/opt/backups/byf_muhendislik/`

**Retention:** 30 gün (daha eski backup'lar otomatik silinir)

**Kullanım:**
```bash
sudo bash backup_production.sh
```

---

### `restore_backup.sh` 📦
**Amaç:** Backup'tan geri yükleme yapar.

**⚠️ UYARI:** Mevcut database'i siler!

**Kullanım:**
```bash
sudo bash restore_backup.sh
```

---

### `monitoring.sh` 🔍
**Amaç:** Sunucu sağlık kontrolü yapar.

**Kontrol eder:**
- Sistem kaynakları (CPU, RAM, Disk)
- Servis durumları
- Web site erişilebilirliği
- SSL sertifikası geçerliliği
- Database durumu
- Son hatalar

**Kullanım:**
```bash
sudo bash monitoring.sh
```

---

## 🔧 Environment Variables (.env)

### Şablon Dosya
```
deployment/.env.example
```

### Production'da Konum
```
/opt/byf_muhendislik/backend/.env
```

### Önemli Değişkenler

**Güvenlik:**
- `SECRET_KEY` - Django secret key (otomatik oluşturulur)
- `DEBUG` - Production'da **False** olmalı
- `ALLOWED_HOSTS` - Domain adınız
- `CSRF_TRUSTED_ORIGINS` - HTTPS URL'leriniz

**Database:**
- `DB_NAME` - byf_muhendislik
- `DB_USER` - byf_user
- `DB_PASSWORD` - Güçlü şifre
- `DB_HOST` - localhost

**Cache:**
- `REDIS_URL` - redis://localhost:6379/0

**Email:**
- `EMAIL_HOST` - smtp.gmail.com
- `EMAIL_HOST_USER` - Gmail hesabınız
- `EMAIL_HOST_PASSWORD` - App-specific password

---

## 🎯 Deployment Stratejisi

### Geliştirme Ortamı (Local)
```
1. Kod değişikliği yap
2. Test et (python manage.py runserver)
3. Git commit + push
```

### Production Ortamı (VPS)
```
1. SSH ile bağlan
2. deploy_production.sh çalıştır
3. Test et
4. Monitor et
```

### Rollback (Geri Alma)
```bash
# Önceki commit'e dön
cd /opt/byf_muhendislik
git log --oneline -10
git checkout COMMIT_HASH

# Deploy et
cd deployment/scripts
sudo bash deploy_production.sh

# VEYA backup'tan restore et
sudo bash restore_backup.sh
```

---

## 📊 Monitoring ve Maintenance

### Günlük Kontroller
```bash
# Servis durumları
systemctl status byf_gunicorn nginx postgresql redis-server

# Disk kullanımı
df -h

# RAM kullanımı
free -h

# Sunucu monitoring
sudo bash monitoring.sh
```

### Haftalık Kontroller
- Backup'ların alındığını kontrol et
- Log dosyalarını incele
- SSL sertifikası süresini kontrol et

### Aylık Kontroller
- Güvenlik güncellemelerini yükle: `apt update && apt upgrade`
- Backup'ları test et (restore yaparak)
- Performans metrikleri

---

## 🔐 Güvenlik En İyi Uygulamalar

### 1. SSH Güvenliği
- [ ] SSH key authentication kullan
- [ ] Root login'i kapat
- [ ] Fail2ban aktif
- [ ] SSH portunu değiştir (opsiyonel)

### 2. Application Güvenliği
- [ ] DEBUG=False
- [ ] SECRET_KEY güçlü ve gizli
- [ ] ALLOWED_HOSTS sadece domain'iniz
- [ ] HTTPS zorunlu
- [ ] HSTS aktif

### 3. Database Güvenliği
- [ ] Güçlü şifre kullan
- [ ] Sadece localhost'tan erişim
- [ ] Düzenli backup

### 4. Firewall
- [ ] UFW aktif
- [ ] Sadece gerekli portlar açık (22, 80, 443)

---

## 🆘 Sorun Giderme

### Gunicorn Çalışmıyor
```bash
# Status kontrol
systemctl status byf_gunicorn

# Log kontrol
journalctl -u byf_gunicorn -n 100 --no-pager

# Restart
systemctl restart byf_gunicorn
```

### Nginx 502 Bad Gateway
```bash
# Gunicorn çalışıyor mu?
systemctl status byf_gunicorn

# Socket var mı?
ls -la /opt/byf_muhendislik/gunicorn.sock

# Nginx error log
tail -f /var/log/nginx/byf_error.log
```

### Static Files Yüklenmiyor
```bash
cd /opt/byf_muhendislik/backend
source ../venv/bin/activate
python manage.py collectstatic --noinput

# Permission düzelt
chown -R www-data:www-data staticfiles/
chmod -R 755 staticfiles/
```

---

## 📞 Destek

**Logları topla:**
```bash
sudo bash << 'EOF'
tar -czf /tmp/byf_logs_$(date +%Y%m%d).tar.gz \
    /var/log/byf/ \
    /var/log/nginx/byf_*.log \
    /opt/byf_muhendislik/backend/.env
EOF

# İndir ve destek ekibiyle paylaş
```

---

## ✅ Deployment Checklist

### İlk Kurulum
- [ ] VPS satın alındı ve hazır
- [ ] Domain DNS ayarları yapıldı
- [ ] SSH bağlantısı kuruldu
- [ ] Proje dosyaları yüklendi
- [ ] setup_server.sh çalıştırıldı
- [ ] SSL sertifikası kuruldu
- [ ] Admin kullanıcısı oluşturuldu
- [ ] Email ayarları yapıldı
- [ ] Backup cron job eklendi
- [ ] Monitoring kuruldu
- [ ] Site test edildi

### Her Deployment Sonrası
- [ ] Backup alındı
- [ ] deploy_production.sh çalıştırıldı
- [ ] Migration uyarıları kontrol edildi
- [ ] Static files toplandı
- [ ] Gunicorn restart edildi
- [ ] Health check başarılı
- [ ] Admin panel çalışıyor
- [ ] Genel site çalışıyor
- [ ] Log dosyaları temiz

---

## 🎉 Başarılı Deployment!

Projeniz başarıyla canlıya alındı!

**Yararlı Linkler:**
- Site: https://yourdomain.com
- Admin: https://yourdomain.com/admin/
- SSL Test: https://www.ssllabs.com/ssltest/

**Komutlar:**
```bash
# Durum kontrolü
sudo bash /opt/byf_muhendislik/deployment/scripts/monitoring.sh

# Yeni deployment
sudo bash /opt/byf_muhendislik/deployment/scripts/deploy_production.sh

# Backup
sudo bash /opt/byf_muhendislik/deployment/scripts/backup_production.sh
```

---

**İyi çalışmalar! 🚀**

**Son Güncelleme:** 2024  
**Proje:** BYF Mühendislik  
**Hedef Sunucu:** Hostinger KVM1 (4GB RAM, 1 vCPU, 50GB, Germany)


