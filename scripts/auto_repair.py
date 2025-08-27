#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "db.sqlite"

def main():
    if not DB.exists():
        print("ℹ️  DB absente → bootstrap")
        sys.exit(subprocess.run(["python", str(ROOT / "scripts/bootstrap.py")]).returncode)
    conn = sqlite3.connect(DB)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cur.fetchone():
            print("ℹ️  Schéma incomplet → bootstrap")
            conn.close()
            sys.exit(subprocess.run(["python", str(ROOT / "scripts/bootstrap.py")]).returncode)
        # Safe columns on sources
        try: conn.execute("ALTER TABLE sources ADD COLUMN error_count INTEGER DEFAULT 0")
        except Exception: pass
        try: conn.execute("ALTER TABLE sources ADD COLUMN is_active INTEGER DEFAULT 1")
        except Exception: pass
        conn.commit()
        print("✅ Auto-repair OK"); sys.exit(0)
    finally:
        try: conn.close()
        except Exception: pass

if __name__ == "__main__":
    main()