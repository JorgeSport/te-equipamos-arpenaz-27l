from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "news-data.json"
OWN_FILE = BASE / "te-equipamos-content.json"
MADRID = ZoneInfo("Europe/Madrid")
NOW = datetime.now(timezone.utc)
MAX_AGE = timedelta(days=10)
MAX_ITEMS = 24

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TeEquipamosNews/1.1; +https://jorgesport.github.io/)"
}

GOOGLE = "https://news.google.com/rss/search?q={q}&hl=es&gl=ES&ceid=ES:es"


def gnews(query: str) -> str:
    return GOOGLE.format(q=urllib.parse.quote(query))


FEEDS = [
    {
        "name": "RUNNEA",
        "url": "https://www.runnea.com/rss/articulos.xml",
        "category": "Deportes",
        "quality": 13,
    },
    {
        "name": "Montaña y senderismo",
        "url": gnews('(senderismo OR trekking OR montañismo OR alpinismo) when:7d'),
        "category": "Outdoor",
        "quality": 11,
    },
    {
        "name": "Trail running",
        "url": gnews('(trail running OR ultratrail OR carreras por montaña) when:7d'),
        "category": "Deportes",
        "quality": 11,
    },
    {
        "name": "Ciclismo",
        "url": gnews('(ciclismo OR MTB OR gravel OR mountain bike) when:7d'),
        "category": "Deportes",
        "quality": 11,
    },
    {
        "name": "Camping y aventura",
        "url": gnews('(camping OR acampada OR aventura outdoor OR actividades al aire libre) when:7d'),
        "category": "Outdoor",
        "quality": 9,
    },
    {
        "name": "Equipamiento outdoor",
        "url": gnews('(equipamiento montaña OR botas trekking OR mochila senderismo OR ropa técnica outdoor OR material trail) when:7d'),
        "category": "Novedades",
        "quality": 12,
    },
    {
        "name": "Outdoor España",
        "url": gnews('((senderismo OR montaña OR trail OR ciclismo) España) when:7d'),
        "category": "España",
        "quality": 10,
    },
    {
        "name": "Outdoor internacional",
        "url": gnews('(Everest OR Himalaya OR Alpes OR expedición montaña OR alpinismo internacional) when:7d'),
        "category": "Internacional",
        "quality": 10,
    },
    {
        "name": "Tecnología outdoor",
        "url": gnews('(Garmin OR Suunto OR GPS senderismo OR e-bike OR reloj deportivo OR tecnología outdoor) when:7d'),
        "category": "Tecnología",
        "quality": 12,
    },
    {
        "name": "Escalada y expediciones",
        "url": gnews('(escalada OR expedición montaña OR cumbre alpinismo) when:7d'),
        "category": "Outdoor",
        "quality": 9,
    },
]

FALLBACK_IMAGES = {
    "Outdoor": "https://images.unsplash.com/photo-1464822759844-d150baec0494?auto=format&fit=crop&w=1200&q=82",
    "Deportes": "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?auto=format&fit=crop&w=1200&q=82",
    "Novedades": "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1200&q=82",
    "España": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=82",
    "Tecnología": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=82",
    "Internacional": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=82",
}

REJECT = {
    "amazon", "temu", "aliexpress", "black friday", "cupón", "cupon", "código descuento",
    "codigo descuento", "chollo", "apuestas", "casino", "horóscopo", "horoscopo"
}

MIN_PER_CATEGORY = {
    "Outdoor": 4,
    "Deportes": 4,
    "Novedades": 3,
    "España": 2,
    "Internacional": 2,
    "Tecnología": 2,
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<script.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def trim(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    cut = value[: limit - 1].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def parse_date(value: str | None) -> datetime:
    if not value:
        return NOW
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return NOW


def stable_id(url: str) -> int:
    return int(hashlib.sha1(url.encode("utf-8")).hexdigest()[:8], 16)


def norm_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-záéíóúüñ0-9 ]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def is_duplicate(title: str, existing: list[dict]) -> bool:
    a = set(norm_title(title).split())
    if not a:
        return True
    for item in existing:
        b = set(norm_title(item.get("title", "")).split())
        if not b:
            continue
        similarity = len(a & b) / max(1, min(len(a), len(b)))
        if similarity >= 0.78:
            return True
    return False


def is_stale_title(title: str) -> bool:
    current_year = NOW.astimezone(MADRID).year
    years = [int(y) for y in re.findall(r"\b20\d{2}\b", title)]
    return any(year < current_year - 1 for year in years)


def image_from_item(item: ET.Element, description: str, category: str) -> str:
    for element in item.iter():
        tag = element.tag.lower()
        url = element.attrib.get("url", "")
        typ = element.attrib.get("type", "")
        if url and (("image" in typ.lower()) or tag.endswith("thumbnail") or tag.endswith("content")):
            if url.startswith("http"):
                return url
    match = re.search(r'<img[^>]+src=["\']([^"\']+)', description or "", flags=re.I)
    if match and match.group(1).startswith("http"):
        return unescape(match.group(1))
    return FALLBACK_IMAGES.get(category, FALLBACK_IMAGES["Outdoor"])


def source_from_item(item: ET.Element, default: str) -> str:
    for child in item:
        if child.tag.lower().endswith("source") and clean_html(child.text):
            return trim(clean_html(child.text), 55)
    return default


def node_text(item: ET.Element, endings: tuple[str, ...]) -> str:
    for child in item:
        tag = child.tag.lower()
        if any(tag.endswith(ending) for ending in endings):
            if child.text:
                return child.text.strip()
    return ""


def link_from_item(item: ET.Element) -> str:
    direct = node_text(item, ("link",))
    if direct.startswith("http"):
        return direct
    for child in item:
        if child.tag.lower().endswith("link"):
            href = child.attrib.get("href", "")
            if href.startswith("http"):
                return href
    return ""


def refine_category(category: str, title: str) -> str:
    low = title.lower()
    tech = ("garmin", "suunto", "gps", "reloj", "smartwatch", "e-bike", "ebike", "motor", "sensor", "app ")
    gear = ("zapatilla", "bota", "mochila", "chaqueta", "material", "equipamiento", "casco", "tienda de campaña")
    if category not in {"España", "Internacional"} and any(k in low for k in tech):
        return "Tecnología"
    if category in {"Outdoor", "Deportes"} and any(k in low for k in gear):
        return "Novedades"
    return category


def make_summary(title: str, raw_description: str, source: str, category: str) -> tuple[str, str]:
    desc = clean_html(raw_description)
    title_key = norm_title(title)[:55]
    desc_key = norm_title(desc)[:100]
    useful = len(desc) >= 70 and title_key not in desc_key
    if useful:
        summary = trim(desc, 250)
        details = trim(desc, 520)
        if details == summary:
            details = f"{source} ha publicado esta información dentro de la actualidad de {category.lower()}. Te Equipamos la incorpora a su selección editorial por su interés para quienes practican actividades al aire libre."
        return summary, details
    summary = f"Actualidad de {category.lower()} seleccionada por Te Equipamos a partir de la información publicada por {source}."
    details = "Consulta la fuente original para conocer el contexto completo, datos, declaraciones y posibles actualizaciones de esta información."
    return summary, details


def format_time(dt: datetime) -> str:
    months = {1:"ene",2:"feb",3:"mar",4:"abr",5:"may",6:"jun",7:"jul",8:"ago",9:"sep",10:"oct",11:"nov",12:"dic"}
    local = dt.astimezone(MADRID)
    return f"{local.day} {months[local.month]} {local.year} · {local:%H:%M}"


def parse_feed(config: dict) -> list[dict]:
    xml = fetch(config["url"])
    root = ET.fromstring(xml)
    nodes = [n for n in root.iter() if n.tag.lower().endswith("item") or n.tag.lower().endswith("entry")]
    output = []
    for item in nodes[:40]:
        title = clean_html(node_text(item, ("title",)))
        link = link_from_item(item)
        if not title or not link:
            continue
        source = source_from_item(item, config["name"])
        if source and title.lower().endswith(" - " + source.lower()):
            title = title[: -(len(source) + 3)].strip()
        low = title.lower()
        if any(word in low for word in REJECT) or is_stale_title(title):
            continue
        raw_desc = node_text(item, ("description", "summary", "content"))
        pub = node_text(item, ("pubdate", "published", "updated", "date"))
        dt = parse_date(pub)
        if NOW - dt > MAX_AGE:
            continue
        category = refine_category(config["category"], title)
        summary, details = make_summary(title, raw_desc, source, category)
        age_hours = max(0, (NOW - dt).total_seconds() / 3600)
        score = max(50, 100 + config.get("quality", 0) - int(age_hours / 8))
        output.append({
            "id": stable_id(link),
            "title": trim(title, 155),
            "summary": summary,
            "details": details,
            "category": category,
            "source": source,
            "time": format_time(dt),
            "url": link,
            "image": image_from_item(item, raw_desc, category),
            "featured": False,
            "score": score,
            "published_ts": dt.timestamp(),
        })
    return output


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def prepare_owned() -> list[dict]:
    owned = []
    for item in load_json(OWN_FILE, []):
        if not item.get("active", True):
            continue
        row = dict(item)
        row["owned"] = True
        row.setdefault("source", "Te Equipamos")
        row.setdefault("category", "Novedades")
        row.setdefault("image", FALLBACK_IMAGES.get(row["category"], FALLBACK_IMAGES["Outdoor"]))
        row.setdefault("score", 94)
        row.setdefault("featured", False)
        row.setdefault("time", "Contenido Te Equipamos")
        row.setdefault("details", row.get("summary", "Contenido propio de Te Equipamos."))
        if not row.get("id"):
            row["id"] = stable_id(row.get("url", row.get("title", "te-equipamos")))
        owned.append(row)
    return owned[:5]


def can_add(item: dict, selected: list[dict], source_counts: dict) -> bool:
    if source_counts.get(item["source"], 0) >= 4:
        return False
    if is_duplicate(item["title"], selected):
        return False
    return True


def add_item(item: dict, selected: list[dict], source_counts: dict) -> None:
    selected.append(item)
    source_counts[item["source"]] = source_counts.get(item["source"], 0) + 1


def main() -> None:
    fallback = load_json(DATA_FILE, [])
    candidates = []
    errors = []
    for config in FEEDS:
        try:
            candidates.extend(parse_feed(config))
        except Exception as exc:
            errors.append(f"{config['name']}: {exc}")

    candidates.sort(key=lambda x: (x.get("score", 0), x.get("published_ts", 0)), reverse=True)
    selected: list[dict] = []
    source_counts: dict[str, int] = {}

    # Primero garantiza variedad para que todas las categorías que ya existen en el diseño tengan contenido.
    for category, minimum in MIN_PER_CATEGORY.items():
        added = 0
        for item in candidates:
            if item["category"] != category or not can_add(item, selected, source_counts):
                continue
            add_item(item, selected, source_counts)
            added += 1
            if added >= minimum:
                break

    # Después completa la portada con la actualidad más reciente y relevante.
    for item in candidates:
        if len(selected) >= MAX_ITEMS:
            break
        if not can_add(item, selected, source_counts):
            continue
        add_item(item, selected, source_counts)

    if len(selected) < 8:
        print(f"Solo se obtuvieron {len(selected)} noticias automáticas; se conserva la edición de respaldo.")
        selected = [dict(x) for x in fallback]
    else:
        selected.sort(key=lambda x: (x.get("score", 0), x.get("published_ts", 0)), reverse=True)
        for item in selected[:4]:
            item["featured"] = True
        for item in selected:
            item.pop("published_ts", None)

    owned = prepare_owned()
    # Distribuye reviews/landings propias entre noticias externas: presencia comercial sin saturar.
    slots = [6, 12, 18, 24, 28]
    for own, slot in zip(owned, slots):
        selected.insert(min(slot, len(selected)), own)

    selected = selected[: MAX_ITEMS + len(owned)]
    DATA_FILE.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = {}
    for item in selected:
        counts[item.get("category", "Otros")] = counts.get(item.get("category", "Otros"), 0) + 1
    print(f"Te Equipamos News: {len(selected)} contenidos preparados ({len(owned)} propios).")
    print("Distribución:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    if errors:
        print("Fuentes que no respondieron (se ignoran sin romper la web):")
        for error in errors:
            print(" -", error)


if __name__ == "__main__":
    main()
