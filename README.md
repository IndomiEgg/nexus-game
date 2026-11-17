# NEXUS.GAME — Portal Berita Game

Flask + SQLAlchemy + APScheduler. Berita RSS otomatis tiap 30 menit + artikel orisinal lewat panel admin.

## Struktur
```
app/            kode aplikasi (models, routes, services, templates, static)
config/         settings.py (env) dan feeds.py (daftar RSS & kategori)  <- edit sumber RSS di sini
database/       schema.sql (PostgreSQL + index) dan seed.sql (kategori + 3 artikel contoh)
scripts/        export_schema.py (buat ulang schema.sql dari model)
wsgi.py         entry point gunicorn
```

## Jalankan lokal
```
pip install -r requirements.txt
python -c "from wsgi import app; app.run(debug=True)"
```
Tanpa `DATABASE_URL`, aplikasi memakai SQLite (`instance/nexus.db`). Admin: `/admin` (default admin / admin123, WAJIB diganti).

## Database
`create_all` + `seed.sql` dijalankan otomatis saat start. Untuk membuat manual di PostgreSQL:
`psql $DATABASE_URL -f database/schema.sql -f database/seed.sql`

## Ganti password admin
Set environment variable `ADMIN_USER` dan `ADMIN_PASSWORD` (di dashboard hosting atau `.env`).

## Tambah / hapus sumber RSS
Edit `FEEDS` di `config/feeds.py`, lalu deploy ulang. Sumber yang dihapus otomatis dinonaktifkan.

## Deploy gratis tanpa kartu: Vercel + GitHub Actions + Neon
- Vercel menjalankan website (entrypoint `wsgi.py`). Env di Vercel: DATABASE_URL, DATABASE_URL_UNPOOLED (opsional), SECRET_KEY, ADMIN_USER, ADMIN_PASSWORD, SITE_URL.
- RSS diambil `.github/workflows/refresh-rss.yml` tiap 30 menit. Tambahkan secret DATABASE_URL (dan DATABASE_URL_UNPOOLED) di GitHub: Settings > Secrets and variables > Actions.
- Jalankan manual sekali: tab Actions > Refresh RSS > Run workflow.
