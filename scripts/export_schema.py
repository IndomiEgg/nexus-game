"""Hasilkan database/schema.sql (PostgreSQL) dari model, supaya SQL selalu sinkron dengan kode."""
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.extensions import db
from app import models  # noqa: F401

lines = ["-- NEXUS.GAME - skema database (PostgreSQL). Dibuat otomatis: python -m scripts.export_schema", ""]
for table in db.metadata.sorted_tables:
    lines.append(str(CreateTable(table).compile(dialect=postgresql.dialect())).strip() + ";")
    lines += [str(CreateIndex(i).compile(dialect=postgresql.dialect())).strip() + ";" for i in sorted(table.indexes, key=lambda i: i.name)]
    lines.append("")
Path("database/schema.sql").write_text("\n".join(lines), encoding="utf-8")
print("schema.sql ditulis")
