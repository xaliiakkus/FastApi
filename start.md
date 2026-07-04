# Local

1. `.env.example` dosyasini `.env` olarak kopyala
2. `.env` icine Atlas connection string'i yaz
3. Calistir:

```bash
uvicorn main:app --reload --host 0.0.0.0
```

# MongoDB Atlas (Railway icin)

Railway'de **MongoDB servisi ekleme**. Sadece su variable'lari FastAPI servisine ekle:

```
MONGODB_URI=mongodb+srv://KULLANICI:SIFRE@cluster0.okyk1jy.mongodb.net/?appName=Cluster0
MONGODB_DB=app
MONGODB_USERS_COLLECTION=users
SECRET_KEY=uzun-rastgele-bir-deger
METRICS_API_KEY=opsiyonel-guvenlik-anahtari
```

**Onemli:** Sifrede ozel karakter varsa URI icinde encode et.
Ornek: `34Patron47&` -> `34Patron47%26`

Atlas'ta **Network Access** kisminda Railway IP'lerine izin ver:
- Gecici test: `0.0.0.0/0` (Allow access from anywhere)
- Production: Railway outbound IP'lerini sinirla

# Railway deploy

1. GitHub repo'yu Railway'e bagla
2. FastAPI servisinde yukaridaki variable'lari ayarla
3. `PORT` degiskenini elle ekleme (Railway otomatik verir)

Deploy sonrasi:
- Health: `GET /health` (mongodb durumunu da gosterir)
- API docs: `/docs`
- Metrikler: `GET /api/metrics`
- Loglar: `GET /api/logs?limit=100`

METRICS_API_KEY tanimliysa header:
`X-Metrics-Key: <anahtar>`
