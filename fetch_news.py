"""Trae titulares de Google News RSS, deduplica y escribe data.json. Solo stdlib."""
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

GNEWS = "https://news.google.com/rss/search?q={q}&hl=es-419&gl=PE&ceid=PE:es-419"

CATEGORIES = {
    "cancilleria": [
        'cancillería Perú OR "relaciones exteriores" Perú',
        '"política exterior" Perú OR embajador Perú',
    ],
    "economia": [
        '"economía global" OR "economía mundial"',
        'FMI OR "Banco Mundial" OR "Reserva Federal" aranceles OR crecimiento',
    ],
    "conflictos": [
        'guerra Ucrania OR Rusia',
        'Gaza OR Israel OR "Medio Oriente" conflicto',
        'guerra OR conflicto armado internacional',
    ],
    "eeuu": [
        '"Estados Unidos" política exterior',
        '"Casa Blanca" OR "Departamento de Estado" OR Washington',
    ],
    "europa": [
        '"Unión Europea" política',
        'OTAN OR Bruselas OR Europa diplomacia',
    ],
    "asia": [
        'China OR Japón OR India OR Corea diplomacia OR "política exterior"',
    ],
    "latinoamerica": [
        '"América Latina" OR Latinoamérica política',
        'México OR Brasil OR Argentina OR Colombia OR Chile gobierno OR elecciones',
    ],
}

MAX_PER_CATEGORY = 30
MAX_AGE_DAYS = 7


def fetch_feed(query):
    url = GNEWS.format(q=urllib.parse.quote(query))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return ET.fromstring(r.read())


def normalize(title):
    # ponytail: dedupe por titulo normalizado, suficiente para RSS
    return re.sub(r"[^a-z0-9áéíóúñ]+", "", title.lower())


def parse_items(root):
    for item in root.iter("item"):
        title = item.findtext("title", "")
        source = item.findtext("source", "")
        # Google News agrega " - Fuente" al final del titulo
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)]
        try:
            date = parsedate_to_datetime(item.findtext("pubDate", ""))
        except (ValueError, TypeError):
            date = None
        yield {
            "title": title.strip(),
            "link": item.findtext("link", ""),
            "source": source,
            "date": date.isoformat() if date else None,
        }


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    seen = set()
    out = {}
    for cat, queries in CATEGORIES.items():
        items = []
        for q in queries:
            try:
                root = fetch_feed(q)
            except Exception as e:
                print(f"  [warn] feed fallo ({q!r}): {e}")
                continue
            for it in parse_items(root):
                key = normalize(it["title"])
                if not key or key in seen:
                    continue
                if it["date"] and datetime.fromisoformat(it["date"]) < cutoff:
                    continue
                seen.add(key)
                items.append(it)
        items.sort(key=lambda x: x["date"] or "", reverse=True)
        out[cat] = items[:MAX_PER_CATEGORY]
        print(f"{cat}: {len(out[cat])} titulares")

    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "categories": out,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
    # self-check
    d = json.load(open("data.json", encoding="utf-8"))
    assert d["categories"], "sin categorias"
    titles = [normalize(i["title"]) for c in d["categories"].values() for i in c]
    assert len(titles) == len(set(titles)), "hay titulares repetidos"
    print("OK, sin repetidos")
