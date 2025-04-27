# Edremit Nöbetçi Eczane API

Bu uygulama, Edremit Belediyesi web sitesinden nöbetçi eczane bilgilerini çeker, PostgreSQL veritabanında saklar ve bir API aracılığıyla sunar.

# DIKKAT

Bu uygulama sadece web scrapping yapisini ogrenmek icin kurgulanmis olup siteyi olabildigince az mesgul etmek hedeflenmistir.

## Özellikler

- Her gün saat 15:00'da otomatik olarak nöbetçi eczane bilgilerini günceller
- Eczane ve nöbetçi bilgilerini ayrı tablolarda saklar (mükerrer kayıtları önler)
- FastAPI ile geliştirilmiş modern ve performanslı API
- Docker ile kolay kurulum ve çalıştırma imkanı
- Detaylı loglama sistemi

## Kurulum

### Gereksinimler

- Docker ve Docker Compose

### Kurulum Adımları

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullaniciadi/edremit-nobetci-eczane.git
cd edremit-nobetci-eczane
```

2. Docker Compose ile uygulamayı başlatın:
```bash
docker-compose up -d
```

## API Kullanımı

API'ye http://localhost:8000 adresinden erişebilirsiniz.

### API Dokümantasyonu

API dokümantasyonuna http://localhost:8000/docs adresinden erişebilirsiniz.

### Örnek API İstekleri

#### Bugünün Nöbetçi Eczaneleri

```
GET /api/nobetci-eczaneler
```

#### Belirli Bir Tarihteki Nöbetçi Eczaneler

```
GET /api/nobetci-eczaneler?tarih=2023-04-27
```

#### Belirli Bir Bölgedeki Nöbetçi Eczaneler

```
GET /api/nobetci-eczaneler?bolge=MERKEZ
```

#### Koordinat Bilgisi Olan Nöbetçi Eczaneler

```
GET /api/nobetci-eczaneler?koordinat=true
```

#### Tüm Eczaneleri Listele

```
GET /api/eczaneler
```

#### Kayıtlı Tüm Bölgeleri Listele

```
GET /api/bolgeler
```

#### Harita İçin Eczane Bilgilerini Al

```
GET /api/eczaneler/harita-bilgileri
```

#### Sadece Nöbetçi Eczanelerin Harita Bilgilerini Al

```
GET /api/eczaneler/harita-bilgileri?sadece_nobetci=true
```

#### Adres Kullanarak Eczane Koordinatlarını Güncelle

```
POST /api/eczaneler/{eczane_id}/adresle-koordinat-bul
```

#### Manuel Olarak Eczane Koordinatlarını Güncelle

```
POST /api/eczaneler/{eczane_id}/koordinat-guncelle?latitude=37.123&longitude=27.456
```

## Proje Yapısı

```
microservices_architecture/
├── requirements.txt
├── docker-compose.yml
├── README.md
├── .env
├── run_scraper.py
├── run_api.py
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── parser.py
│   │   └── scheduler.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── eczane.py
│   │   └── deps.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
└── logs/
    └── app.log
```

## Veritabanı Yapısı

Uygulama iki temel tablo kullanır:

1. **Eczaneler**: Tüm eczanelerin temel bilgileri
   - id (PK)
   - bolge
   - isim
   - konum_url
   - adres
   - telefon
   - latitude (enlem)
   - longitude (boylam)
   - created_at
   - updated_at

2. **Nöbetçi Eczaneler**: Hangi eczanenin hangi tarihte nöbetçi olduğu bilgisi
   - id (PK)
   - eczane_id (FK)
   - tarih
   - not_bilgisi
   - created_at

## Lisans

MIT


### POSTGRESQL ICIN SQL KOMUTLARI



-- Veritabanını oluştur
CREATE DATABASE eczane_db;

-- Veritabanına bağlan
\c eczane_db;

-- Eczaneler tablosu
CREATE TABLE eczaneler (
    id SERIAL PRIMARY KEY,
    bolge VARCHAR(100) NOT NULL,
    isim VARCHAR(150) NOT NULL UNIQUE,
    konum_url TEXT,
    adres TEXT,
    telefon VARCHAR(20),
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nöbetçi Eczaneler tablosu
CREATE TABLE nobetci_eczaneler (
    id SERIAL PRIMARY KEY,
    eczane_id INTEGER NOT NULL REFERENCES eczaneler(id) ON DELETE CASCADE,
    tarih DATE NOT NULL,
    not_bilgisi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_eczane_tarih UNIQUE (eczane_id, tarih)
);

-- updated_at sütunu için trigger fonksiyonu
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Eczaneler tablosu için güncelleme trigger'ı
CREATE TRIGGER update_eczaneler_updated_at
BEFORE UPDATE ON eczaneler
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Eczaneler için indeks
CREATE INDEX idx_eczaneler_bolge ON eczaneler(bolge);
CREATE INDEX idx_eczaneler_coordinates ON eczaneler(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Nöbetçi eczaneler için indeks
CREATE INDEX idx_nobetci_eczaneler_tarih ON nobetci_eczaneler(tarih);
CREATE INDEX idx_nobetci_eczaneler_eczane_id ON nobetci_eczaneler(eczane_id);