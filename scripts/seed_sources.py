#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sqlite3, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "db.sqlite"
SOURCES = ROOT / "data_sources" / "config_sources.json"

def main():
    if not SOURCES.exists():
        print("ℹ️  Pas de fichier sources."); return
    try:
        cfg = json.loads(SOURCES.read_text(encoding="utf-8"))
        conn = sqlite3.connect(DB); cur = conn.cursor()
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
        conn.commit(); conn.close()
        print(f"✅ Sources sync: +{inserted} / ~{updated}")
    except Exception as e:
        print(f"❌ Seed sources: {e}"); sys.exit(2)

if __name__ == "__main__":
    main()