# Online Sınav Sistemi (YDG Projesi)

Yazılım Doğrulama ve Geçerleme dersi için geliştirilmiş kapsamlı online sınav sistemi.

## 🚀 Hızlı Başlangıç

### Docker ile Çalıştırma

```bash
# Tüm servisleri başlat
docker-compose up --build

# Uygulamaya eriş: http://localhost:8000
```

### Local Geliştirme

```bash
# Virtual environment oluştur
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı başlat
uvicorn app.main:app --reload
```

## 📋 Proje Yapısı

```
YDG/
├── app/                    # Ana uygulama
│   ├── models/            # Veritabanı modelleri
│   ├── schemas/           # Pydantic şemaları
│   ├── routers/           # API endpoint'leri
│   ├── services/          # İş mantığı
│   └── templates/         # Jinja2 şablonları
├── tests/                  # Test dosyaları
│   ├── unit/              # Unit testler
│   ├── integration/       # Integration testler
│   └── e2e/               # Selenium E2E testler
├── docker/                 # Docker yapılandırması
├── docker-compose.yml      # Konteyner orkestrasyonu
└── Jenkinsfile            # CI/CD pipeline
```

## 👥 Kullanıcı Rolleri

| Rol | Yetkiler |
|-----|----------|
| Admin | Sınav oluşturma, soru ekleme, sonuçları görme |
| Öğrenci | Sınavları görme, sınava girme, sonuç görme |

## 🧪 Test Çalıştırma

```bash
# Unit testler
pytest tests/unit/ -v

# Integration testler
pytest tests/integration/ -v

# E2E testler (Selenium)
pytest tests/e2e/ -v
```

## 📦 Teknolojiler

- **Backend**: Python FastAPI
- **Frontend**: Jinja2 Templates
- **Database**: PostgreSQL
- **CI/CD**: Jenkins
- **Container**: Docker & docker-compose
- **Testing**: pytest, Selenium

## 📄 Lisans

Bu proje YDG dersi için eğitim amaçlı geliştirilmiştir.
