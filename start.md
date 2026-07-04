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

**Deploy hatasi `poetry could not be found`:** Dashboard > Service > Settings > Start Command alanini **bos birak**. Poetry yok.

**Deploy hatasi `PORT is not a valid integer`:** Start Command alanini **bos birak**. Port ayari Dockerfile CMD icinde (`sh -c` ile `${PORT}` expand edilir).

Deploy sonrasi:
- Health: `GET /health` (mongodb durumunu da gosterir)
- API docs: `/docs`
- Metrikler: `GET /api/metrics`
- Loglar: `GET /api/logs?limit=100`

METRICS_API_KEY tanimliysa header:
`X-Metrics-Key: <anahtar>`

# Railway CLI (Windows)

## Kurulum (Windows)

Scoop yoksa npm kullan:

```powershell
npm install -g @railway/cli
railway --version
```

Alternatif (Scoop kuruluysa): `scoop install railway`

## Ilk deploy

Proje klasorunde:

```powershell
cd C:\Users\heimdal\Desktop\FastApi

# Tarayicida login
railway login

# Yeni proje olustur
railway init

# Atlas + app ayarlari
railway variables set MONGODB_URI="mongodb+srv://xaliakkus_db_user:34Patron47%26@cluster0.okyk1jy.mongodb.net/?appName=Cluster0"
railway variables set MONGODB_DB="trafficbuddy"
railway variables set MONGODB_USERS_COLLECTION="users"
railway variables set SECRET_KEY="uzun-rastgele-bir-deger"

# Deploy
railway up

# Public URL al
railway domain
```

## Sik kullanilan komutlar

```powershell
railway status          # proje durumu
railway logs            # canli loglar
railway logs --build    # build loglari
railway variables       # env listesi
railway redeploy        # son deploy'u tekrar calistir
railway open            # dashboard ac
```

## Lokal test (Railway env ile)

```powershell
railway run uvicorn main:app --reload --host 0.0.0.0
```

Railway'deki variable'lari lokal ortamda kullanir.

## Mevcut Railway projesine baglan

Dashboard'da proje zaten varsa:

```powershell
railway link
railway up
```
