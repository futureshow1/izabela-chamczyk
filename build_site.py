#!/usr/bin/env python3
"""Build script v2: uses full-size first images as thumbnails when WP resized versions are 404."""

import json
import os
import urllib.request
import urllib.parse
import ssl
import re
from pathlib import Path

BASE = Path(__file__).parent
THUMBS = BASE / "images" / "thumbs"
WORKS_IMG = BASE / "images" / "works"
NEWS_IMG = BASE / "images" / "news"
WP = "http://izabelachamczyk.com/wp-content/uploads/"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        # URL-encode the path portion for special characters
        parsed = urllib.parse.urlparse(url)
        encoded_path = urllib.parse.quote(parsed.path, safe='/:@')
        encoded_url = urllib.parse.urlunparse(parsed._replace(path=encoded_path))
        req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        return False

CATEGORIES = {
    "malarstwo": {"title_pl": "Malarstwo", "title_en": "Painting", "parent_pl": "prace", "parent_en": "works"},
    "video": {"title_pl": "Video", "title_en": "Video", "parent_pl": "prace", "parent_en": "works"},
    "instalacje": {"title_pl": "Instalacje", "title_en": "Installations", "parent_pl": "prace", "parent_en": "works"},
    "fotografia": {"title_pl": "Fotografia", "title_en": "Photography", "parent_pl": "prace", "parent_en": "works"},
    "performance": {"title_pl": "Performance", "title_en": "Performance", "parent_pl": "akcje", "parent_en": "actions"},
    "wojna": {"title_pl": "Wojna Dwunastomiesięczna", "title_en": "Twelve-Month War", "parent_pl": "akcje", "parent_en": "actions"},
    "warsztaty": {"title_pl": "Warsztaty", "title_en": "Workshops", "parent_pl": "akcje", "parent_en": "actions"},
}

def esc(s):
    """Escape HTML entities."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def make_page(lang, title, css_path, js_path, nav_prefix, home, body_html):
    if lang == "pl":
        nav = f"""      <nav class="main-nav">
        <ul>
          <li><a href="{nav_prefix}prace.html">Prace</a></li>
          <li><a href="{nav_prefix}akcje.html">Akcje</a></li>
          <li><a href="{nav_prefix}aktualnosci.html">Aktualności</a></li>
          <li><a href="{nav_prefix}bio.html">Bio</a></li>
          <li><a href="{nav_prefix}kontakt.html">Kontakt</a></li>
          <li><a href="{nav_prefix}en/index.html">English</a></li>
        </ul>
      </nav>"""
    else:
        nav = f"""      <nav class="main-nav">
        <ul>
          <li><a href="{nav_prefix}works.html">Works</a></li>
          <li><a href="{nav_prefix}actions.html">Actions</a></li>
          <li><a href="{nav_prefix}news.html">News</a></li>
          <li><a href="{nav_prefix}bio.html">Bio</a></li>
          <li><a href="{nav_prefix}contact.html">Contact</a></li>
          <li><a href="{nav_prefix}../index.html">Polski</a></li>
        </ul>
      </nav>"""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} | Izabela Chamczyk</title>
  <link rel="stylesheet" href="{css_path}">
  <script src="{js_path.replace('main.js','auth.js')}"></script>
</head>
<body>
  <div class="wrapper">
    <header class="site-header">
      <button class="hamburger" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
{nav}
      <div class="site-title">
        <a href="{home}">Izabela Chamczyk</a>
      </div>
    </header>
    <main>
{body_html}
    </main>
    <footer class="site-footer">
      &copy; 2026 / <a href="{home}">Izabela Chamczyk</a> / <a href="#">Credits</a>
    </footer>
  </div>
  <script src="{js_path}"></script>
</body>
</html>
"""


def get_thumb_path(slug, works_by_slug):
    """Get thumbnail: use downloaded thumb or fall back to first work image."""
    # Check if we have a downloaded thumbnail
    # Try finding any file in thumbs that could match
    for f in THUMBS.iterdir():
        if f.is_file() and f.stat().st_size > 0:
            # Match by slug in various ways
            pass

    # Better approach: use first full-size image downloaded for this work
    if slug in works_by_slug:
        imgs = works_by_slug[slug].get("images", [])
        if imgs:
            fname = imgs[0].split("/")[-1]
            local = WORKS_IMG / f"{slug}_{fname}"
            if local.exists() and local.stat().st_size > 0:
                return f"images/works/{slug}_{fname}"
    return None


def main():
    # Load data
    paintings_file = BASE / "chamczyk_paintings_data.json"
    works_file = BASE / "chamczyk_works_data.json"

    with open(paintings_file) as f:
        paintings = json.load(f)
    with open(works_file) as f:
        works_raw = json.load(f)

    all_works = {
        "malarstwo": paintings,
        "video": works_raw.get("VIDEO", []),
        "instalacje": works_raw.get("INSTALACJE", []),
        "fotografia": works_raw.get("FOTOGRAFIA", []),
        "performance": works_raw.get("PERFORMANCE", []),
        "wojna": works_raw.get("WOJNA_DWUNASTOMIESIECZNA", works_raw.get("WOJNA DWUNASTOMIESIECZNA", [])),
        "warsztaty": works_raw.get("WARSZTATY", []),
    }

    # Build slug lookup
    works_by_slug = {}
    for cat, wlist in all_works.items():
        for w in wlist:
            works_by_slug[w["slug"]] = w

    # Download full-size first images as thumbnails for works missing thumbs
    print("=== Downloading work images (for thumbnails + detail pages) ===")
    WORKS_IMG.mkdir(parents=True, exist_ok=True)
    ok = fail = skip = 0
    for cat_key, wlist in all_works.items():
        for w in wlist:
            slug = w["slug"]
            for i, img_url in enumerate(w.get("images", [])[:3]):
                fname = img_url.split("/")[-1]
                dest = WORKS_IMG / f"{slug}_{fname}"
                if dest.exists() and dest.stat().st_size > 0:
                    skip += 1
                    continue
                if download(img_url, dest):
                    ok += 1
                else:
                    fail += 1
                    print(f"  FAIL: {slug} - {fname}")
    print(f"Work images: {ok} new, {skip} cached, {fail} failed")

    # Download wojna thumbnail images specifically
    print("\n=== Downloading wojna thumbnails ===")
    wojna_thumbs = {
        "11-walka-o-niezaleznosc": "2018/10/11.jpg",
        "10-walka-z-materia": "2018/10/IMG_9227_131010.jpg",
        "9-walka-z-konstrukcja": "2014/06/mini_e.jpg",
        "8-walka-ze-zlymi-myslami": "2014/06/min_1m.jpg",
        "7-walka-o-odpowiedni-czas-i-miejsce": "2014/06/mini_3.jpg",
        "06-rebeliancka-walka-o-przestrzen": "2014/06/03_pp.jpg",
        "05-partyzancka-walka-o-przetrwanie": "2014/06/05.jpg",
        "04-walka-z-bezradnoscia": "2014/06/miniG.jpg",
        "03-walka-o-uporzadkowanie": "2014/06/mini_t2.jpg",
        "02-walka-z-cialem": "2014/06/mini_p.jpg",
        "01-walka-o-siebie": "2014/05/walka1_kwadrat.jpg",
    }
    THUMBS.mkdir(parents=True, exist_ok=True)
    for slug, path in wojna_thumbs.items():
        url = WP + path
        fname = path.split("/")[-1]
        dest = THUMBS / f"wojna_{fname}"
        if download(url, dest):
            print(f"  OK: {fname}")
        else:
            print(f"  FAIL: {fname}")

    # Generate gallery pages
    print("\n=== Generating gallery pages ===")
    for cat_key, wlist in all_works.items():
        if not wlist:
            print(f"  SKIP: {cat_key} (empty)")
            continue
        cat = CATEGORIES[cat_key]

        for lang in ["pl", "en"]:
            title = cat["title_pl"] if lang == "pl" else cat["title_en"]
            parent = cat["parent_pl"] if lang == "pl" else cat["parent_en"]

            if lang == "pl":
                css_path = "css/style.css"
                js_path = "js/main.js"
                nav_prefix = ""
                home = "index.html"
                img_prefix = ""
            else:
                css_path = "../css/style.css"
                js_path = "../js/main.js"
                nav_prefix = ""
                home = "index.html"
                img_prefix = "../"

            cards = []
            for w in wlist:
                slug = w["slug"]
                wtitle = w["title"]
                # Find thumbnail image
                thumb = None
                imgs = w.get("images", [])
                if imgs:
                    fname = imgs[0].split("/")[-1]
                    local = WORKS_IMG / f"{slug}_{fname}"
                    if local.exists() and local.stat().st_size > 0:
                        thumb = f"{img_prefix}images/works/{slug}_{fname}"

                if not thumb:
                    continue

                detail_path = f"{parent}/{cat_key}/{slug}.html"
                cards.append(f"""      <a href="{detail_path}" class="category-card">
        <img src="{thumb}" alt="{esc(wtitle)}">
      </a>""")

            body = f"""      <h1 class="page-title">{esc(title)}</h1>
      <div class="category-grid gallery-grid">
{chr(10).join(cards)}
      </div>"""

            html = make_page(lang, title, css_path, js_path, nav_prefix, home, body)

            if lang == "pl":
                path = BASE / f"{cat_key}.html"
            else:
                path = BASE / "en" / f"{cat_key}.html"
            path.write_text(html, encoding="utf-8")

        print(f"  {cat_key}: {len(wlist)} works")

    # Generate detail pages
    print("\n=== Generating detail pages ===")
    for cat_key, wlist in all_works.items():
        cat = CATEGORIES[cat_key]

        for lang in ["pl", "en"]:
            parent = cat["parent_pl"] if lang == "pl" else cat["parent_en"]
            cat_title = cat["title_pl"] if lang == "pl" else cat["title_en"]

            if lang == "pl":
                detail_dir = BASE / parent / cat_key
                css_path = "../../css/style.css"
                js_path = "../../js/main.js"
                nav_prefix = "../../"
                home = "../../index.html"
                back_path = f"../../{cat_key}.html"
            else:
                detail_dir = BASE / "en" / parent / cat_key
                css_path = "../../../css/style.css"
                js_path = "../../../js/main.js"
                nav_prefix = "../../"
                home = "../../index.html"
                back_path = f"../../../en/{cat_key}.html"

            detail_dir.mkdir(parents=True, exist_ok=True)

            for w in wlist:
                slug = w["slug"]
                wtitle = w["title"]
                desc = w.get("description", "")
                images = w.get("images", [])
                youtube = w.get("youtube_embed", "")
                vimeo = w.get("vimeo_embed", "")
                video_embed = w.get("video_embed", "")

                # Build content
                parts = []
                parts.append(f'      <a href="{back_path}" class="back-link">&larr; {esc(cat_title)}</a>')
                parts.append(f'      <h1 class="work-title">{esc(wtitle)}</h1>')

                # Video embed
                if youtube:
                    parts.append(f'      <div class="work-video"><iframe src="{youtube}" allowfullscreen></iframe></div>')
                elif vimeo:
                    parts.append(f'      <div class="work-video"><iframe src="{vimeo}" allowfullscreen></iframe></div>')
                elif video_embed:
                    parts.append(f'      <div class="work-video"><iframe src="{video_embed}" allowfullscreen></iframe></div>')

                # Images
                for img_url in images:
                    fname = img_url.split("/")[-1]
                    if lang == "pl":
                        img_path = f"../../images/works/{slug}_{fname}"
                    else:
                        img_path = f"../../../images/works/{slug}_{fname}"
                    parts.append(f'      <div class="work-image"><img src="{img_path}" alt="{esc(wtitle)}"></div>')

                # Description
                if desc:
                    desc_paras = []
                    for line in desc.split("\n"):
                        line = line.strip()
                        if line:
                            desc_paras.append(f"        <p>{esc(line)}</p>")
                    if desc_paras:
                        parts.append(f'      <div class="work-description">')
                        parts.extend(desc_paras)
                        parts.append(f'      </div>')

                body = "\n".join(parts)
                html = make_page(lang, wtitle, css_path, js_path, nav_prefix, home, body)
                (detail_dir / f"{slug}.html").write_text(html, encoding="utf-8")

        print(f"  {cat_key}: {len(wlist)} detail pages (PL + EN)")

    # Update prace.html and akcje.html with proper links
    print("\n=== Updating prace.html and akcje.html ===")

    # prace.html - links to malarstwo, video, instalacje, fotografia
    prace_cards = [
        ("malarstwo.html", "images/cat-malarstwo.png", "Malarstwo"),
        ("video.html", "images/cat-video.png", "Video"),
        ("instalacje.html", "images/cat-instalacje.png", "Instalacje"),
        ("fotografia.html", "images/cat-fotografia.png", "Fotografia"),
    ]
    prace_body = '      <div class="category-grid cols-4">\n'
    for href, img, label in prace_cards:
        prace_body += f"""        <a href="{href}" class="category-card">
          <img src="{img}" alt="{label}">
        </a>
"""
    prace_body += '      </div>'
    html = make_page("pl", "Prace", "css/style.css", "js/main.js", "", "index.html", prace_body)
    (BASE / "prace.html").write_text(html, encoding="utf-8")

    # akcje.html
    akcje_cards = [
        ("performance.html", "images/cat-performance.png", "Performance"),
        ("wojna.html", "images/cat-wojna.png", "Wojna Dwunastomiesięczna"),
        ("warsztaty.html", "images/cat-warsztaty.png", "Warsztaty"),
    ]
    akcje_body = '      <div class="category-grid">\n'
    for href, img, label in akcje_cards:
        akcje_body += f"""        <a href="{href}" class="category-card">
          <img src="{img}" alt="{label}">
        </a>
"""
    akcje_body += '      </div>'
    html = make_page("pl", "Akcje", "css/style.css", "js/main.js", "", "index.html", akcje_body)
    (BASE / "akcje.html").write_text(html, encoding="utf-8")

    # en/works.html
    works_cards = [
        ("malarstwo.html", "../images/cat-malarstwo.png", "Painting"),
        ("video.html", "../images/cat-video.png", "Video"),
        ("instalacje.html", "../images/cat-instalacje.png", "Installations"),
        ("fotografia.html", "../images/cat-fotografia.png", "Photography"),
    ]
    works_body = '      <div class="category-grid cols-4">\n'
    for href, img, label in works_cards:
        works_body += f"""        <a href="{href}" class="category-card">
          <img src="{img}" alt="{label}">
        </a>
"""
    works_body += '      </div>'
    html = make_page("en", "Works", "../css/style.css", "../js/main.js", "", "index.html", works_body)
    (BASE / "en" / "works.html").write_text(html, encoding="utf-8")

    # en/actions.html
    actions_cards = [
        ("performance.html", "../images/cat-performance.png", "Performance"),
        ("wojna.html", "../images/cat-wojna.png", "Twelve-Month War"),
        ("warsztaty.html", "../images/cat-warsztaty.png", "Workshops"),
    ]
    actions_body = '      <div class="category-grid">\n'
    for href, img, label in actions_cards:
        actions_body += f"""        <a href="{href}" class="category-card">
          <img src="{img}" alt="{label}">
        </a>
"""
    actions_body += '      </div>'
    html = make_page("en", "Actions", "../css/style.css", "../js/main.js", "", "index.html", actions_body)
    (BASE / "en" / "actions.html").write_text(html, encoding="utf-8")

    # Update index.html homepage links
    print("\n=== Updating homepage links ===")
    index_cards = [
        ("prace.html", "images/cat-malarstwo.png", "Malarstwo", "works.html"),
        ("akcje.html", "images/cat-performance.png", "Performance", "actions.html"),
        ("prace.html", "images/cat-video.png", "Video", "works.html"),
    ]
    # PL index - just update the category grid links
    index_html = (BASE / "index.html").read_text(encoding="utf-8")
    # Replace href="#" with actual links in category cards
    index_html = index_html.replace('href="works.html" class="category-card"', 'href="prace.html" class="category-card"')
    index_html = index_html.replace('href="actions.html" class="category-card"', 'href="akcje.html" class="category-card"')
    (BASE / "index.html").write_text(index_html, encoding="utf-8")

    print("\n=== Generating aktualnosci.html with real images ===")
    news_body = """      <h1 class="page-title">Aktualności</h1>
      <div class="news-list">
        <div class="news-item">
          <div class="news-date">28.09.2022 — 08.01.2023</div>
          <div class="news-text">
            <p>Wystawa zbiorowa podsumowująca 20 lat konkursu Artystyczna Podróż Hestii:</p>
          </div>
          <h2 class="news-title"><a href="https://artystycznapodrozhestii.pl/exhibition/bujnosc-atlas-nieskonczonych-mozliwosci-komentarz-artystycznej-podrozy-hestii/" target="_blank">"Bujność. Atlas nieskończonych możliwości"</a></h2>
          <div class="news-subtitle">Wystawa w Państwowej Galerii Sztuki w Sopocie</div>
          <div class="news-image"><img src="images/news/ok.jpg" alt="Bujność exhibition"></div>
        </div>

        <div class="news-item">
          <div class="news-date">27.11.2021 — 21.01.2022</div>
          <div class="news-text">
            <p>indywidualna wystawa malarstwa performatywnego pt. TOXIC</p>
          </div>
          <div class="news-subtitle"><a href="https://www.galeriafoksal.pl/home/" target="_blank">Galeria Foksal Warszawa</a></div>
          <div class="news-image"><img src="images/news/str.jpg" alt="TOXIC exhibition"></div>
          <div class="news-text">
            <p><em>"Zajmuję się sztuką, ponieważ nie umiem inaczej. Sztuka jest moją pasją i życiem. Dzięki niej wypowiadam się, przerabiam ważne tematy i stwarzam nowe rzeczywistości. Bycie artystką traktuję jako mój zawód, ale jest to też moja tożsamość. Na pytanie kim jestem? — odpowiadam — artystką."</em></p>
            <p>Więcej na temat mojej twórczości można znaleźć na stronie <a href="https://secondaryarchive.org/artists/izabela-chamczyk/" target="_blank">SECONDARY ARCHIVE</a> — Archiwum artystek stworzonym we współpracy z Fundacją Katarzyny Kozyry oraz Zachętą Narodową Galerią Sztuki, w którym się znalazłam.</p>
          </div>
          <div class="news-image"><img src="images/news/secondary.png" alt="Secondary Archive"></div>
        </div>

        <div class="news-item">
          <div class="news-text">
            <p>Dziesięć z moich dokumentacji performance znalazło się w <a href="https://artmuseum.pl/pl/archiwum/archiwum-polskiego-performansu/3147" target="_blank">ARCHIWUM POLSKIEGO PERFORMANSU</a> w Muzeum Sztuki Nowoczesnej w Warszawie</p>
          </div>
          <div class="news-image"><img src="images/news/Zrzut-ekranu-2021-01-14-o-11.25.28.png" alt="Archiwum Polskiego Performansu"></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">Wystawa indywidualna pt. "SERIOUSLY SALTY. Nowe materializacje"</h2>
          <div class="news-subtitle"><a href="https://www.entropia.art.pl/view_news.php?id=599" target="_blank">Galeria Entropia, Wrocław</a> 08.10 — 05.11.2020</div>
          <div class="news-image"><img src="images/news/3.-Seriously-salty.-Nowe-materializacje_Laptopy_z-cyklu-Destruction-is-Creation+video_Szum-uderzenia.jpg" alt="Seriously Salty exhibition"></div>
          <div class="news-text"><p>fot. Andrzej Rerak</p></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">Wystawa online pt. "PRZESTRZEŃ ZAMKNIĘTA/OTWARTA"</h2>
          <div class="news-text">
            <p>Gdzie prezentowane są zdjęcia z procesu tworzenia moich OBRAZÓW PERFORMATYWNYCH</p>
            <p>kurator: Grzegorz Borkowski</p>
            <p><a href="http://odaart.pl/oda_przestrzenzamknieta/wirtualna-wystawa/#1" target="_blank">Galeria ODA Piotrków Trybunalski</a></p>
          </div>
          <div class="news-image"><img src="images/news/czerwony_20200225_171130.jpg" alt="Przestrzeń Zamknięta/Otwarta"></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">Izabela Chamczyk. Koniec Końców — performance online</h2>
          <div class="news-date">piątek, 28.08.2020, godz. 17:00</div>
          <div class="news-text">
            <p>Trzeci performance online w ramach cyklu "CODZIENNOŚĆ". Cykl performance Izabeli Chamczyk odnosi się do sytuacji pandemii i nawiązuje do aktualnych wydarzeń. Każde kolejne działanie jest odpowiedzią na zmieniającą się rzeczywistość. Poprzez medium ciała artystka oddaje stan, kondycję i emocje społeczne.</p>
            <p>transmisja na Facebooku <a href="https://www.facebook.com/bwawroclawglowny/" target="_blank">BWA Wrocław Główny</a> oraz <a href="https://www.facebook.com/bwa.wroclaw/" target="_blank">BWA Wrocław</a></p>
            <p>Partnerzy: <a href="https://www.facebook.com/lokal30/" target="_blank">lokal_30</a> w Warszawie, <a href="https://www.facebook.com/cswkronika/" target="_blank">CSW Kronika</a> w Bytomiu, BWA Wrocław</p>
            <p>Zrealizowano w ramach programu stypendialnego Ministra Kultury i Dziedzictwa Narodowego — Kultura w sieci.</p>
          </div>
          <div class="news-image"><a href="https://www.gov.pl/web/kultura"><img src="images/news/image001.jpg" alt="MKiDN" style="max-width:150px"></a></div>
        </div>

        <div class="news-item">
          <div class="news-text">
            <p>Zapraszam na wystawę online PRZESTRZEŃ OTWARTA/ZAMKNIĘTA, gdzie prezentowane jest moje malarstwo performatywne</p>
            <p>kurator: Grzegorz Borkowski</p>
            <p><a href="http://odaart.pl/oda_przestrzenzamknieta/glowna/" target="_blank">Galeria ODA Piotrków Trybunalski</a></p>
            <p>Malarstwo performatywne powstało dzięki wsparciu Stypendium z Fundusz Popierania Twórczości ZAiKS</p>
          </div>
        </div>

        <div class="news-item">
          <h2 class="news-title">Złoty środek — performance online</h2>
          <div class="news-date">29.07.2020, godz. 17:00</div>
          <div class="news-text">
            <p>Drugi performance online w ramach cyklu "CODZIENNOŚĆ". Cykl performance Izabeli Chamczyk odnosi się do sytuacji pandemii i nawiązuje do aktualnych wydarzeń. Każde kolejne działanie jest odpowiedzią na zmieniającą się rzeczywistość. Poprzez medium ciała artystka oddaje stan, kondycję i emocje społeczne.</p>
            <p>transmisja na Facebooku galeria <a href="https://www.facebook.com/lokal30/" target="_blank">lokal_30</a></p>
            <p>Partnerzy: lokal_30 w Warszawie, CSW Kronika w Bytomiu, BWA Wrocław</p>
            <p>Zrealizowano w ramach programu stypendialnego Ministra Kultury i Dziedzictwa Narodowego — Kultura w sieci.</p>
          </div>
          <div class="news-image"><a href="https://www.gov.pl/web/kultura"><img src="images/news/image001.jpg" alt="MKiDN" style="max-width:150px"></a></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">Początek końca — performance online</h2>
          <div class="news-date">26.06.2020, godz. 17:00</div>
          <div class="news-text">
            <p>Pierwszy performance online w ramach cyklu "CODZIENNOŚĆ". Cykl performance odnosi się do sytuacji pandemii i nawiązuje do aktualnych wydarzeń. Każde kolejne działanie jest odpowiedzią na zmieniającą się rzeczywistość. Poprzez medium ciała artystka oddaje stan, kondycję i emocje społeczne.</p>
            <p>transmisja na Facebooku <a href="https://www.facebook.com/cswkronika/" target="_blank">Kronika</a></p>
            <p>Partnerzy: CSW Kronika w Bytomiu, lokal_30 w Warszawie, BWA Awangarda we Wrocławiu.</p>
            <p>Zrealizowano w ramach programu stypendialnego Ministra Kultury i Dziedzictwa Narodowego — Kultura w sieci.</p>
          </div>
          <div class="work-video"><iframe src="https://www.youtube.com/embed/bzVTUu2QWr0" allowfullscreen></iframe></div>
          <div class="news-image"><a href="https://www.gov.pl/web/kultura/"><img src="images/news/500.jpg" alt="MKiDN" style="max-width:100px"></a></div>
        </div>
      </div>"""

    html = make_page("pl", "Aktualności", "css/style.css", "js/main.js", "", "index.html", news_body)
    (BASE / "aktualnosci.html").write_text(html, encoding="utf-8")

    # EN news page
    news_body_en = """      <h1 class="page-title">News</h1>
      <div class="news-list">
        <div class="news-item">
          <div class="news-date">November 27th 2021 — January 21st 2022</div>
          <div class="news-text">
            <p>individual exhibition of performative painting entitled TOXIC</p>
          </div>
          <div class="news-subtitle"><a href="https://www.galeriafoksal.pl/en/home/" target="_blank">Foksal Gallery Warsaw</a></div>
          <div class="news-image"><img src="../images/news/str.jpg" alt="TOXIC exhibition"></div>
          <div class="news-text">
            <p><em>"I do art because I do not know how to do otherwise. Art is my passion and my life. Thanks to it I express myself, process important topics and create new realities. Being an artist is my profession, but it is also my identity. When asked who am I? — I answer — an artist."</em></p>
            <p>More about my work can be found on the <a href="https://secondaryarchive.org/artists/izabela-chamczyk/" target="_blank">SECONDARY ARCHIVE</a> website — created in cooperation with the Katarzyna Kozyra Foundation and Zachęta National Gallery of Art, to which I was included.</p>
          </div>
          <div class="news-image"><img src="../images/news/secondary.png" alt="Secondary Archive"></div>
        </div>

        <div class="news-item">
          <div class="news-text">
            <p>Ten of my documentation of performances can be found in <a href="https://artmuseum.pl/en/archiwum/archiwum-polskiego-performansu/3147" target="_blank">POLISH PERFORMANCE ARCHIVE</a> at the Museum of Modern Art in Warsaw</p>
          </div>
          <div class="news-image"><img src="../images/news/Zrzut-ekranu-2021-01-14-o-11.29.14.png" alt="Polish Performance Archive"></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">Individual exhibition "SERIOUSLY SALTY. New materialisations."</h2>
          <div class="news-subtitle"><a href="https://www.entropia.art.pl/view_news.php?id=599" target="_blank">Entropia Gallery Wrocław</a> 08.10 — 05.11.2020</div>
          <div class="news-image"><img src="../images/news/3.-Seriously-salty.-Nowe-materializacje_Laptopy_z-cyklu-Destruction-is-Creation+video_Szum-uderzenia.jpg" alt="Seriously Salty exhibition"></div>
          <div class="news-text"><p>phot. Andrzej Rerak</p></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">GOLDEN MEAN — online performance by Izabela Chamczyk</h2>
          <div class="news-date">29.07.2020, at 5 pm</div>
          <div class="news-text">
            <p>The second online performance from the "EVERYDAY LIFE" cycle. Izabela Chamczyk's cycle of performances relates to the pandemic and current events. Each action is a response to the changing reality. Using her body as a medium, the artist reflects the social situation, condition and emotions.</p>
            <p>live streaming on Facebook <a href="https://www.facebook.com/lokal30/" target="_blank">lokal_30</a></p>
            <p>Partners: CCA Kronika in Bytom, lokal_30 in Warsaw, BWA Awangarda in Wrocław</p>
            <p>Supported by the scholarship programme of the Minister of Culture and National Heritage "Kultura w sieci/Culture in the Net".</p>
          </div>
          <div class="news-image"><a href="https://www.gov.pl/web/kultura"><img src="../images/news/image001.jpg" alt="MKiDN" style="max-width:150px"></a></div>
        </div>

        <div class="news-item">
          <h2 class="news-title">The beginning of the end — online performance</h2>
          <div class="news-date">26.06.2020, at 5 pm</div>
          <div class="news-text">
            <p>The first online performance of the "EVERYDAY LIFE" cycle. Cycle of performances relates to the pandemic and current events. Each action is a response to the changing reality. Using her body as a medium, the artist reflects the social situation, condition and emotions.</p>
            <p>live streaming on Facebook <a href="https://www.facebook.com/cswkronika/" target="_blank">Kronika</a></p>
            <p>Partners: CCA Kronika in Bytom, lokal_30 in Warsaw, BWA Awangarda in Wrocław.</p>
            <p>Supported by the scholarship programme of the Minister of Culture and National Heritage "Kultura w sieci/Culture in the Net".</p>
          </div>
          <div class="news-image"><a href="https://www.gov.pl/web/kultura/"><img src="../images/news/500.jpg" alt="MKiDN" style="max-width:100px"></a></div>
        </div>
      </div>"""

    html = make_page("en", "News", "../css/style.css", "../js/main.js", "", "index.html", news_body_en)
    (BASE / "en" / "news.html").write_text(html, encoding="utf-8")

    print("\n=== SUMMARY ===")
    total = sum(len(w) for w in all_works.values())
    print(f"Total works: {total}")
    for k, v in all_works.items():
        print(f"  {k}: {len(v)}")

    # Count files
    html_count = len(list(BASE.rglob("*.html")))
    img_count = len(list((BASE / "images").rglob("*")))
    print(f"Total HTML files: {html_count}")
    print(f"Total image files: {img_count}")


if __name__ == "__main__":
    main()
