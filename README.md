# FastApi Projesi

Bu proje FastAPI, SQLAlchemy, PostgreSQL ve Alembic kullanılarak geliştirilmiştir.

## Kurulum

```bash
poetry install
poetry shell
python -m uvicorn main:app --reload
```
# Compose ile durdur (önerilen)
docker compose down
# Sadece bu container'ı durdur
docker stop FastApi_b
# Durdur + sil
docker rm -f FastApi_b