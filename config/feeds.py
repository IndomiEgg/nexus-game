"""Sumber RSS dan aturan kategori. Edit file ini untuk menambah / menghapus sumber."""

FEEDS = [
    {"name": "IGN", "url": "https://feeds.feedburner.com/ign/games-all", "lang": "en"},
    {"name": "GameSpot", "url": "https://www.gamespot.com/feeds/news/", "lang": "en"},
    {"name": "PC Gamer", "url": "https://www.pcgamer.com/rss/", "lang": "en"},
    {"name": "Eurogamer", "url": "https://www.eurogamer.net/feed", "lang": "en"},
    {"name": "Kotaku", "url": "https://kotaku.com/rss", "lang": "en"},
    {"name": "Gamebrott", "url": "https://gamebrott.com/feed", "lang": "id"},
    {"name": "Duniaku", "url": "https://www.duniaku.net/feed", "lang": "id"},
]

# Urutan = prioritas. Slug harus ada di tabel categories (lihat database/seed.sql).
CATEGORY_RULES = [
    ("esports", r"esports?|tournament|championship|valorant|dota|league of legends|mlbb|turnamen"),
    ("review", r"review|ulasan|hands-on"),
    ("mobile", r"mobile|android|\bios\b|iphone|genshin|honor of kings"),
    ("pc", r"\bpc\b|steam|nvidia|\bamd\b|epic games|windows"),
    ("console", r"playstation|\bps[45]\b|xbox|nintendo|switch"),
    ("indie", r"indie"),
    ("industry", r"layoff|studio|acquisition|earnings|\bceo\b|revenue|akuisisi"),
]
DEFAULT_CATEGORY = "general"
