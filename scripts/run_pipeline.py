#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "db.sqlite"
OUT = ROOT / "frontend" / "pages" / "updates"

def ensure_tables(conn):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS sources(name TEXT PRIMARY KEY, url TEXT, type TEXT, is_active INTEGER DEFAULT 1, created_at TEXT, error_count INTEGER DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT, title TEXT, url TEXT UNIQUE, content TEXT, publication_date TEXT, content_hash TEXT UNIQUE, metadata TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS findings(id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id INTEGER, topic TEXT, summary TEXT, classification_data TEXT, confidence REAL, practical_impact TEXT, created_at TEXT)")
    conn.commit()

def active_sources(conn):
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, url, type FROM sources WHERE COALESCE(is_active,1)=1")
        return cur.fetchall()
    except sqlite3.OperationalError:
        return []

def simulate_fetch(name, url):
    now = datetime.now(timezone.utc).isoformat()
    title = f"Update {name} - {now[:10]}"
    content = f"Contenu simulé pour {name} à {now}."
    link = f"{url}#simulated"  # URL stable -> déduplication par URL
    pub = now[:10]
    return title, content, link, pub

def main():
    if not DB.exists():
        print("❌ DB absente. Exécutez scripts/bootstrap.py"); sys.exit(2)

    conn = sqlite3.connect(DB)
    ensure_tables(conn)
    cur = conn.cursor()

    sources = active_sources(conn)
    if not sources:
        print("ℹ️  Aucune source active."); sys.exit(0)

    created = 0
    for (name, url, stype) in sources[:3]:
        title, content, link, pub = simulate_fetch(name, url)
        content_hash = hashlib.sha256((content or '').encode('utf-8')).hexdigest()

        # Déduplication stricte AVANT insertion (URL puis hash)
        cur.execute("SELECT id FROM documents WHERE url = ?", (link,))
        if cur.fetchone():
            print(f"ℹ️  Document déjà présent (url): {link} → on saute.")
            continue

        cur.execute("SELECT id FROM documents WHERE content_hash = ?", (content_hash,))
        if cur.fetchone():
            print(f"ℹ️  Document déjà présent (hash): {content_hash[:8]}… → on saute.")
            continue

        now_iso = datetime.now(timezone.utc).isoformat()

        # Insertion document
        cur.execute("""
            INSERT INTO documents (source_id, title, url, content, publication_date, content_hash, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, title, link, content, pub, content_hash, json.dumps({'source': name}), now_iso))
        doc_id = cur.lastrowid

        # Insertion finding
        summary = f"TL;DR: Mise à jour détectée pour {name}. Impacts à évaluer."
        cur.execute("""
            INSERT INTO findings (doc_id, topic, summary, classification_data, confidence, practical_impact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, "rgpd", summary, json.dumps({'label':'Pertinent','confidence':0.8}), 0.8, "Moyen", now_iso))

        conn.commit()

        # Génération page statique
        slug = f"{pub}-{name.replace(' ', '-').lower()}"
        OUT.mkdir(parents=True, exist_ok=True)
        astro = f"""---
const title = {json.dumps(title)}
const date = {json.dumps(pub)}
---
<section class="container">
  <h1>{{title}}</h1>
  <p><em>{{date}}</em></p>
  <p>{json.dumps(content)[1:-1]}</p>
  <p><a href="{link}" target="_blank" rel="noopener">Voir la source</a></p>
</section>
"""
        (OUT / f"{slug}.astro").write_text(astro, encoding="utf-8")
        created += 1

    print(f"✅ Pipeline OK. Pages créées: {created}")
    sys.exit(0)

if __name__ == "__main__":
    main()
