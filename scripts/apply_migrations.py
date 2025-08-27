#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "db.sqlite"
MIGRATIONS = ROOT / "storage" / "migrations"

def main():
    try:
        conn = sqlite3.connect(DB)
    except Exception as e:
        print(f"❌ DB: {e}"); sys.exit(1)
    try:
        count=0
        for fp in sorted(MIGRATIONS.glob("*.sql")):
            conn.executescript(fp.read_text(encoding="utf-8")); count+=1
        print(f"✅ {count} migration(s) appliquée(s).")
    except Exception as e:
        print(f"❌ Migrations: {e}"); sys.exit(2)
    finally:
        conn.close()

if __name__ == "__main__":
    main()