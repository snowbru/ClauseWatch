#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialise la base SQLite, applique les migrations, seed l'admin et les sources."""
import json, sqlite3, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "db.sqlite"
SCHEMA = ROOT / "storage" / "schema.sql"
MIGRATIONS = ROOT / "storage" / "migrations"
SOURCES = ROOT / "data_sources" / "config_sources.json"

def exec_sql(conn, sql_text): conn.executescript(sql_text)

def ensure_db(conn):
    try:
        exec_sql(conn, SCHEMA.read_text(encoding="utf-8"))
        print("✅ Base initialisée (schema.sql).")
    except Exception as e:
        print(f"❌ Erreur init DB: {e}"); sys.exit(2)

def apply_migrations(conn):
    if not MIGRATIONS.exists():
        print("ℹ️  Pas de migrations.")
        return
    count=0
    for fp in sorted(MIGRATIONS.glob("*.sql")):
        exec_sql(conn, fp.read_text(encoding="utf-8")); count+=1
    print(f"✅ {count} migration(s) appliquée(s).")

def seed_admin(conn):
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users(email, plan, topics, preferences, email_verified, is_active) VALUES(?,?,?,?,?,?)",
                    ("admin@clausewatch.local","enterprise","[]","{}",1,1))
        conn.commit()
        print("✅ Admin seedé.")
    except Exception as e:
        print(f"❌ Seed admin: {e}"); sys.exit(3)

def seed_sources(conn):
    if not SOURCES.exists():
        print("ℹ️  Aucune source (config_sources.json manquant).")
        return
    try:
        cfg = json.loads(SOURCES.read_text(encoding="utf-8"))
        cur = conn.cursor()
        inserted=updated=0
        for name, meta in cfg.get("sources", {}).items():
            url, stype = meta.get("url"), meta.get("type")
            if not url or not stype: continue
            cur.execute("SELECT id FROM sources WHERE name=?", (name,))
            if cur.fetchone():
                cur.execute("UPDATE sources SET url=?, type=?, is_active=1 WHERE name=?", (url, stype, name)); updated+=1
            else:
                cur.execute("INSERT INTO sources(name,url,type,is_active,created_at) VALUES(?,?,?,?,?)",
                            (name, url, stype, 1, datetime.utcnow().isoformat())); inserted+=1
        conn.commit()
        print(f"✅ Sources: +{inserted} insérées, ~{updated} mises à jour.")
    except Exception as e:
        print(f"❌ Seed sources: {e}"); sys.exit(4)

def main():
    DB.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(DB)
    except Exception as e:
        print(f"❌ Connexion DB: {e}"); sys.exit(1)
    try:
        ensure_db(conn)
        apply_migrations(conn)
        seed_admin(conn)
        seed_sources(conn)
    finally:
        conn.close()
    print(f"🎯 Bootstrap terminé: {DB}")

if __name__ == "__main__":
    main()