#!/usr/bin/env python3
"""Récupère les flux RSS et génère news.json pour le site."""
import json, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Rubrique -> (zone, [flux RSS de secours])
FEEDS = {
    "Politique":    ("fr",  ["https://www.lemonde.fr/rss/politique.xml",
                            "https://www.francetvinfo.fr/politique/titres.rss"]),
    "International":("int", ["https://www.lemonde.fr/rss/international.xml",
                            "https://www.francetvinfo.fr/monde/titres.rss"]),
    "Économie":     ("int", ["https://www.lemonde.fr/rss/economie.xml",
                            "https://www.francetvinfo.fr/economie/titres.rss"]),
    "Société":      ("fr",  ["https://www.lemonde.fr/rss/societe.xml",
                            "https://www.francetvinfo.fr/societe/titres.rss"]),
    "Sport":        ("int", ["https://www.lemonde.fr/rss/sport.xml",
                            "https://www.francetvinfo.fr/sports/titres.rss"]),
    "Planète":      ("int", ["https://www.lemonde.fr/rss/planete.xml",
                            "https://www.francetvinfo.fr/environnement/titres.rss"]),
    "Culture":      ("int", ["https://www.lemonde.fr/rss/culture.xml",
                            "https://www.francetvinfo.fr/culture/titres.rss"]),
}
MAX_PAR_RUBRIQUE = 6
UA = {"User-Agent": "Mozilla/5.0 (compatible; RevueDePresse/1.0)"}

def lire_flux(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):
        def txt(tag):
            e = it.find(tag)
            return (e.text or "").strip() if e is not None and e.text else ""
        items.append({"t": txt("title"), "s": txt("description"),
                      "m": txt("pubDate")[:16], "url": txt("link")})
    return items

articles = []
for rubrique, (zone, urls) in FEEDS.items():
    for url in urls:
        try:
            items = lire_flux(url)
            if items:
                for it in items[:MAX_PAR_RUBRIQUE]:
                    it.update(cat=rubrique, zone=zone)
                    articles.append(it)
                print(f"OK  {rubrique:<13} {len(items):>3} articles  {url}")
                break
        except Exception as e:
            print(f"ÉCHEC {rubrique} {url} -> {e}")

data = {
    "genere_le": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
    "articles": articles,
}
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f"\nnews.json : {len(articles)} articles")
