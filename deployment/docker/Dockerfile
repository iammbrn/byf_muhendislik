# BYF Mühendislik - Django Uygulama Dockerfile
FROM python:3.9-slim

# Environment değişkenleri
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install -r requirements.txt

# Uygulama dosyaları
COPY . .

# Static dosyaları topla
RUN python manage.py collectstatic --noinput

# Port
EXPOSE 8000

# Gunicorn ile çalıştır
CMD ["gunicorn", "byf_muhendislik.wsgi:application", "--bind", "0.0.0.0:8000"]