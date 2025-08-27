#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "db.sqlite"
SOURCES = ROOT / "data_sources" / "config_sources.json"

def main():
    if not DB.exists():
        print("❌ DB manquante. Lancez scripts/bootstrap.py"); sys.exit(2)
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        required = {"users","sources","documents","findings","user_alerts"}
        missing = required - tables
        if missing: print(f"⚠️  Tables manquantes: {missing}")
        else: print("✅ Tables essentielles OK.")
    except Exception as e:
        print(f"❌ DB error: {e}"); sys.exit(3)
    finally:
        try: conn.close()
        except Exception: pass

    if not SOURCES.exists():
        print("⚠️  config_sources.json absent")
    else:
        try:
            json.loads(SOURCES.read_text(encoding="utf-8"))
            print("✅ config_sources.json OK.")
        except Exception as e:
            print(f"❌ config_sources.json invalide: {e}"); sys.exit(4)
    print("🎯 Self-check terminé."); sys.exit(0)

if __name__ == "__main__":
    main()