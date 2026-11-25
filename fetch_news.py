#!/usr/bin/env python3
"""Récupère les flux RSS et génère news.json pour le site."""
import json, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Rubrique -> (zone, [flux RSS : le 1er est essayé, puis les suivants en secours])
FEEDS = {
    "Politique":    ("fr",  ["https://www.lemonde.fr/politique/rss_full.xml",
                             "https://www.francetvinfo.fr/politique.rss",
                             "https://www.franceinfo.fr/politique.rss"]),
    "International":("int", ["https://www.lemonde.fr/international/rss_full.xml",
                             "https://www.francetvinfo.fr/monde.rss",
                             "https://www.franceinfo.fr/monde.rss"]),
    "Économie":     ("int", ["https://www.lemonde.fr/economie/rss_full.xml",
                             "https://www.francetvinfo.fr/economie.rss",
                             "https://www.franceinfo.fr/economie.rss"]),
    "Société":      ("fr",  ["https://www.lemonde.fr/societe/rss_full.xml",
                             "https://www.francetvinfo.fr/societe.rss",
                             "https://www.franceinfo.fr/societe.rss"]),
    "Sport":        ("int", ["https://www.lemonde.fr/sport/rss_full.xml",
                             "https://www.francetvinfo.fr/sports.rss",
                             "https://www.franceinfo.fr/sports.rss"]),
    "Planète":      ("int", ["https://www.lemonde.fr/planete/rss_full.xml",
                             "https://www.francetvinfo.fr/environnement.rss",
                             "https://www.franceinfo.fr/environnement.rss"]),
    "Culture":      ("int", ["https://www.lemonde.fr/culture/rss_full.xml",
                             "https://www.francetvinfo.fr/culture.rss",
                             "https://www.franceinfo.fr/culture.rss"]),
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

# Garde-fou : si rien n'a été récupéré, on ne touche pas à l'ancien news.json
# et on fait échouer le workflow (pastille rouge) pour que ce soit visible.
if not articles:
    print("\nAucun article récupéré : news.json conservé tel quel.")
    sys.exit(1)

data = {
    "genere_le": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
    "articles": articles,
}
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f"\nnews.json : {len(articles)} articles")
