#!/usr/bin/env python3
"""
Simple CMS for Izabela Chamczyk's website.
Run with: python3 admin.py
Then open http://localhost:5000 in your browser.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, unquote
import io
import re as _re
import tempfile

BASE = Path(__file__).parent
DATA_DIR = BASE
IMAGES_DIR = BASE / "images" / "works"
NEWS_IMAGES_DIR = BASE / "images" / "news"
PAINTINGS_FILE = BASE / "chamczyk_paintings_data.json"
WORKS_FILE = BASE / "chamczyk_works_data.json"

CATEGORIES = {
    "malarstwo": {"title": "Malarstwo", "title_en": "Painting", "parent": "prace", "json_key": None},
    "video": {"title": "Video", "title_en": "Video", "parent": "prace", "json_key": "VIDEO"},
    "instalacje": {"title": "Instalacje", "title_en": "Installations", "parent": "prace", "json_key": "INSTALACJE"},
    "fotografia": {"title": "Fotografia", "title_en": "Photography", "parent": "prace", "json_key": "FOTOGRAFIA"},
    "performance": {"title": "Performance", "title_en": "Performance", "parent": "akcje", "json_key": "PERFORMANCE"},
    "wojna": {"title": "Wojna Dwunastomiesięczna", "title_en": "Twelve-Month War", "parent": "akcje", "json_key": "WOJNA_DWUNASTOMIESIECZNA"},
    "warsztaty": {"title": "Warsztaty", "title_en": "Workshops", "parent": "akcje", "json_key": "WARSZTATY"},
}


def load_works(category):
    """Load works for a category."""
    if category == "malarstwo":
        with open(PAINTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(WORKS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        key = CATEGORIES[category]["json_key"]
        return data.get(key, [])


def save_works(category, works):
    """Save works for a category."""
    if category == "malarstwo":
        with open(PAINTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(works, f, ensure_ascii=False, indent=2)
    else:
        with open(WORKS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        key = CATEGORIES[category]["json_key"]
        data[key] = works
        with open(WORKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def slugify(text):
    """Create URL-safe slug from text."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[ąà]', 'a', text)
    text = re.sub(r'[ćč]', 'c', text)
    text = re.sub(r'[ęè]', 'e', text)
    text = re.sub(r'[łl]', 'l', text)
    text = re.sub(r'[ńñ]', 'n', text)
    text = re.sub(r'[óò]', 'o', text)
    text = re.sub(r'[śš]', 's', text)
    text = re.sub(r'[żźž]', 'z', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# ─── HTML Templates ───

STYLE = """
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
  .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 20px; font-weight: 400; }
  .header a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
  .header a:hover { color: #3498db; }
  .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
  .card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
  .card h2 { margin-bottom: 15px; color: #2c3e50; }
  .card h3 { margin-bottom: 10px; color: #555; font-size: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
  .grid-item { background: #f8f9fa; border-radius: 6px; padding: 15px; text-align: center; text-decoration: none; color: #333; transition: all 0.2s; border: 1px solid #e9ecef; }
  .grid-item:hover { background: #e9ecef; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
  .grid-item .count { font-size: 28px; font-weight: 700; color: #3498db; }
  .grid-item .label { font-size: 14px; margin-top: 5px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f8f9fa; font-weight: 600; font-size: 13px; text-transform: uppercase; color: #666; }
  td img { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }
  .btn { display: inline-block; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 14px; cursor: pointer; border: none; transition: all 0.2s; }
  .btn-primary { background: #3498db; color: white; }
  .btn-primary:hover { background: #2980b9; }
  .btn-danger { background: #e74c3c; color: white; }
  .btn-danger:hover { background: #c0392b; }
  .btn-success { background: #27ae60; color: white; }
  .btn-success:hover { background: #219a52; }
  .btn-sm { padding: 4px 10px; font-size: 12px; }
  .form-group { margin-bottom: 18px; }
  .form-group label { display: block; font-weight: 600; margin-bottom: 5px; font-size: 14px; color: #555; }
  .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; font-family: inherit; }
  .form-group textarea { min-height: 120px; resize: vertical; }
  .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #3498db; }
  .form-group small { color: #888; font-size: 12px; }
  .actions { display: flex; gap: 10px; margin-top: 20px; }
  .breadcrumb { margin-bottom: 20px; font-size: 14px; color: #888; }
  .breadcrumb a { color: #3498db; text-decoration: none; }
  .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; }
  .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
  .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
  .thumb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 8px; margin-top: 10px; }
  .thumb-grid img { width: 100%; height: 80px; object-fit: cover; border-radius: 4px; }
  .rebuild-section { text-align: center; padding: 20px; }
  .rebuild-section p { margin-bottom: 15px; color: #666; }
</style>
"""

def page_wrapper(title, content, breadcrumb=""):
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — CMS</title>
  {STYLE}
</head>
<body>
  <div class="header">
    <h1>CMS — Izabela Chamczyk</h1>
    <div>
      <a href="/admin">Panel</a>
      <a href="/admin/news">Aktualności</a>
      <a href="/admin/rebuild">Przebuduj stronę</a>
      <a href="/" target="_blank">Zobacz stronę</a>
    </div>
  </div>
  <div class="container">
    {breadcrumb}
    {content}
  </div>
</body>
</html>"""


def dashboard_page():
    cards = []
    for key, cat in CATEGORIES.items():
        works = load_works(key)
        cards.append(f"""<a href="/admin/category/{key}" class="grid-item">
          <div class="count">{len(works)}</div>
          <div class="label">{cat['title']}</div>
        </a>""")

    return page_wrapper("Panel", f"""
    <div class="card">
      <h2>Kategorie</h2>
      <div class="grid">
        {''.join(cards)}
        <a href="/admin/news" class="grid-item">
          <div class="count">9</div>
          <div class="label">Aktualności</div>
        </a>
      </div>
    </div>
    <div class="card rebuild-section">
      <h2>Przebuduj stronę</h2>
      <p>Po dodaniu lub edycji prac kliknij przycisk poniżej, aby wygenerować nowe pliki HTML.</p>
      <form method="POST" action="/admin/rebuild">
        <button type="submit" class="btn btn-success" style="font-size:16px; padding: 12px 30px;">Przebuduj stronę</button>
      </form>
    </div>
    """)


def category_page(cat_key, message=""):
    cat = CATEGORIES[cat_key]
    works = load_works(cat_key)

    alert = ""
    if message:
        alert = f'<div class="alert alert-success">{message}</div>'

    rows = []
    for i, w in enumerate(works):
        thumb = ""
        if w.get("images"):
            fname = w["images"][0].split("/")[-1]
            local = f"/images/works/{w['slug']}_{fname}"
            thumb = f'<img src="{local}" alt="">'

        video_badge = ""
        if w.get("youtube_embed") or w.get("vimeo_embed") or w.get("video_embed"):
            video_badge = ' <span style="color:#e74c3c">&#9654;</span>'

        rows.append(f"""<tr>
          <td>{thumb}</td>
          <td><strong>{w['title']}</strong>{video_badge}<br><small style="color:#888">{w['slug']}</small></td>
          <td>
            <a href="/admin/category/{cat_key}/edit/{i}" class="btn btn-primary btn-sm">Edytuj</a>
            <a href="/admin/category/{cat_key}/delete/{i}" class="btn btn-danger btn-sm" onclick="return confirm('Usunąć {w["title"]}?')">Usuń</a>
          </td>
        </tr>""")

    bc = f'<div class="breadcrumb"><a href="/admin">Panel</a> &rarr; {cat["title"]}</div>'

    return page_wrapper(cat["title"], f"""
    {alert}
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
        <h2>{cat['title']} ({len(works)})</h2>
        <a href="/admin/category/{cat_key}/add" class="btn btn-primary">+ Dodaj pracę</a>
      </div>
      <table>
        <thead><tr><th style="width:70px">Obraz</th><th>Tytuł</th><th style="width:150px">Akcje</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    """, bc)


def work_form_page(cat_key, work=None, index=None, message="", error=""):
    cat = CATEGORIES[cat_key]
    is_edit = work is not None
    title_val = work["title"] if is_edit else ""
    slug_val = work["slug"] if is_edit else ""
    desc_val = work.get("description", "") if is_edit else ""
    youtube_val = work.get("youtube_embed", "") if is_edit else ""
    vimeo_val = work.get("vimeo_embed", "") if is_edit else ""

    alert = ""
    if message:
        alert = f'<div class="alert alert-success">{message}</div>'
    if error:
        alert = f'<div class="alert alert-error">{error}</div>'

    # Show existing images
    images_html = ""
    if is_edit and work.get("images"):
        thumbs = []
        for img_url in work["images"]:
            fname = img_url.split("/")[-1]
            local = f"/images/works/{work['slug']}_{fname}"
            thumbs.append(f'<img src="{local}" alt="">')
        images_html = f"""
        <div class="form-group">
          <label>Obecne obrazy ({len(work['images'])})</label>
          <div class="thumb-grid">{''.join(thumbs)}</div>
        </div>"""

    action_url = f"/admin/category/{cat_key}/edit/{index}" if is_edit else f"/admin/category/{cat_key}/add"
    action_title = f"Edytuj: {title_val}" if is_edit else "Dodaj nową pracę"

    bc = f'<div class="breadcrumb"><a href="/admin">Panel</a> &rarr; <a href="/admin/category/{cat_key}">{cat["title"]}</a> &rarr; {action_title}</div>'

    return page_wrapper(action_title, f"""
    {alert}
    <div class="card">
      <h2>{action_title}</h2>
      <form method="POST" action="{action_url}" enctype="multipart/form-data">
        <div class="form-group">
          <label>Tytuł</label>
          <input type="text" name="title" value="{title_val}" required>
        </div>
        <div class="form-group">
          <label>Slug (URL)</label>
          <input type="text" name="slug" value="{slug_val}" {'readonly style="background:#f0f0f0"' if is_edit else ''}>
          <small>{'Nie można zmienić po utworzeniu' if is_edit else 'Zostanie wygenerowany automatycznie jeśli puste'}</small>
        </div>
        <div class="form-group">
          <label>Opis</label>
          <textarea name="description">{desc_val}</textarea>
          <small>Każda linia = osobny paragraf. Wpisz technikę, wymiary, rok, info o wystawie, credits.</small>
        </div>
        <div class="form-group">
          <label>YouTube embed URL</label>
          <input type="text" name="youtube_embed" value="{youtube_val}" placeholder="https://www.youtube.com/embed/...">
        </div>
        <div class="form-group">
          <label>Vimeo embed URL</label>
          <input type="text" name="vimeo_embed" value="{vimeo_val}" placeholder="https://player.vimeo.com/video/...">
        </div>
        {images_html}
        <div class="form-group">
          <label>Dodaj obrazy</label>
          <input type="file" name="images" multiple accept="image/*">
          <small>Wybierz jeden lub więcej plików JPG/PNG. Pierwsze zdjęcie będzie miniaturą.</small>
        </div>
        <div class="actions">
          <button type="submit" class="btn btn-primary">{'Zapisz zmiany' if is_edit else 'Dodaj pracę'}</button>
          <a href="/admin/category/{cat_key}" class="btn" style="background:#eee">Anuluj</a>
        </div>
      </form>
    </div>
    """, bc)


def news_page():
    bc = '<div class="breadcrumb"><a href="/admin">Panel</a> &rarr; Aktualności</div>'
    return page_wrapper("Aktualności", f"""
    <div class="card">
      <h2>Aktualności</h2>
      <p style="color:#666; margin-bottom:15px;">
        Aby edytować aktualności, edytuj plik <code>aktualnosci.html</code> bezpośrednio.<br>
        Możesz użyć dowolnego edytora tekstu (np. VS Code, Notepad++).<br>
        Po zmianach kliknij "Przebuduj stronę" — aktualności nie są nadpisywane przy przebudowie.
      </p>
      <p style="color:#666;">
        <strong>Aby dodać nowy wpis:</strong> skopiuj istniejący blok <code>&lt;div class="news-item"&gt;...&lt;/div&gt;</code>
        i zmień tekst, datę i obraz. Obrazy wrzuć do folderu <code>images/news/</code>.
      </p>
    </div>
    """, bc)


def rebuild_page(message="", error=""):
    alert = ""
    if message:
        alert = f'<div class="alert alert-success">{message}</div>'
    if error:
        alert = f'<div class="alert alert-error">{error}</div>'

    bc = '<div class="breadcrumb"><a href="/admin">Panel</a> &rarr; Przebuduj stronę</div>'
    return page_wrapper("Przebuduj stronę", f"""
    {alert}
    <div class="card rebuild-section">
      <h2>Przebuduj stronę</h2>
      <p>To wygeneruje nowe pliki HTML na podstawie danych z JSON.<br>
         Galerie kategorii i strony szczegółowe prac zostaną odtworzone.<br>
         Strona główna, bio, kontakt i aktualności NIE zostaną nadpisane.</p>
      <form method="POST" action="/admin/rebuild">
        <button type="submit" class="btn btn-success" style="font-size:16px; padding: 12px 30px;">Przebuduj stronę</button>
      </form>
    </div>
    """, bc)


class CMSHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quieter logging
        pass

    def send_html(self, html, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def send_redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # Static files (images, css, js)
        if not path.startswith("/admin"):
            file_path = BASE / path.lstrip("/")
            if file_path.is_file():
                ext = file_path.suffix.lower()
                content_types = {
                    ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
                    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                    ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
                    ".ico": "image/x-icon",
                }
                ct = content_types.get(ext, "application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.end_headers()
                self.wfile.write(file_path.read_bytes())
                return
            self.send_response(404)
            self.end_headers()
            return

        # Admin routes
        msg = query.get("msg", [""])[0]

        if path in ("/admin", "/admin/"):
            self.send_html(dashboard_page())

        elif path == "/admin/news":
            self.send_html(news_page())

        elif path == "/admin/rebuild":
            self.send_html(rebuild_page())

        elif path.startswith("/admin/category/") and "/edit/" in path:
            parts = path.split("/")
            cat_key = parts[3]
            index = int(parts[5])
            works = load_works(cat_key)
            if 0 <= index < len(works):
                self.send_html(work_form_page(cat_key, works[index], index, message=msg))
            else:
                self.send_redirect(f"/admin/category/{cat_key}")

        elif path.startswith("/admin/category/") and path.endswith("/add"):
            cat_key = path.split("/")[3]
            self.send_html(work_form_page(cat_key, message=msg))

        elif path.startswith("/admin/category/") and "/delete/" in path:
            parts = path.split("/")
            cat_key = parts[3]
            index = int(parts[5])
            works = load_works(cat_key)
            if 0 <= index < len(works):
                deleted_title = works[index]["title"]
                works.pop(index)
                save_works(cat_key, works)
                self.send_redirect(f"/admin/category/{cat_key}?msg=Usunięto: {deleted_title}")
            else:
                self.send_redirect(f"/admin/category/{cat_key}")

        elif path.startswith("/admin/category/"):
            cat_key = path.split("/")[3]
            if cat_key in CATEGORIES:
                self.send_html(category_page(cat_key, message=msg))
            else:
                self.send_redirect("/admin")

        else:
            self.send_redirect("/admin")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/admin/rebuild":
            try:
                result = subprocess.run(
                    [sys.executable, str(BASE / "build_site.py")],
                    capture_output=True, text=True, cwd=str(BASE), timeout=120
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    summary = "<br>".join(lines[-8:])
                    self.send_html(rebuild_page(message=f"Strona przebudowana!<br><br><code>{summary}</code>"))
                else:
                    self.send_html(rebuild_page(error=f"Błąd: <pre>{result.stderr[:500]}</pre>"))
            except Exception as e:
                self.send_html(rebuild_page(error=f"Błąd: {e}"))
            return

        # Parse form data (multipart or urlencoded)
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")

        form_fields = {}
        uploaded_files = []  # list of (filename, data)

        if "multipart/form-data" in content_type:
            # Extract boundary
            boundary = None
            for part in content_type.split(";"):
                part = part.strip()
                if part.startswith("boundary="):
                    boundary = part[9:].strip('"')
            if boundary:
                boundary_bytes = boundary.encode()
                parts = raw_body.split(b"--" + boundary_bytes)
                for part in parts:
                    if part in (b"", b"--\r\n", b"--"):
                        continue
                    part = part.strip(b"\r\n")
                    if b"\r\n\r\n" not in part:
                        continue
                    header_data, body_data = part.split(b"\r\n\r\n", 1)
                    # Remove trailing boundary markers
                    if body_data.endswith(b"\r\n"):
                        body_data = body_data[:-2]

                    headers_str = header_data.decode("utf-8", errors="replace")
                    # Extract field name and filename
                    name_match = _re.search(r'name="([^"]+)"', headers_str)
                    fname_match = _re.search(r'filename="([^"]*)"', headers_str)

                    if not name_match:
                        continue
                    field_name = name_match.group(1)

                    if fname_match:
                        filename = fname_match.group(1)
                        if filename and len(body_data) > 0:
                            uploaded_files.append((filename, body_data))
                    else:
                        form_fields[field_name] = body_data.decode("utf-8", errors="replace")
        else:
            form_fields = {k: v[0] for k, v in parse_qs(raw_body.decode("utf-8")).items()}

        # Handle add/edit work
        if path.startswith("/admin/category/") and ("/add" in path or "/edit/" in path):
            parts = path.split("/")
            cat_key = parts[3]
            is_edit = "/edit/" in path
            index = int(parts[5]) if is_edit else None

            title = form_fields.get("title", "").strip()
            slug = form_fields.get("slug", "").strip()
            description = form_fields.get("description", "").strip()
            youtube_embed = form_fields.get("youtube_embed", "").strip()
            vimeo_embed = form_fields.get("vimeo_embed", "").strip()

            if not title:
                self.send_html(work_form_page(cat_key, error="Tytuł jest wymagany"))
                return

            if not slug:
                slug = slugify(title)

            works = load_works(cat_key)

            if is_edit and 0 <= index < len(works):
                work = works[index]
            else:
                work = {"slug": slug, "title": "", "description": "", "images": []}
                index = len(works)
                works.append(work)

            work["title"] = title
            work["description"] = description
            if youtube_embed:
                work["youtube_embed"] = youtube_embed
            elif "youtube_embed" in work:
                del work["youtube_embed"]
            if vimeo_embed:
                work["vimeo_embed"] = vimeo_embed
            elif "vimeo_embed" in work:
                del work["vimeo_embed"]

            # Handle uploaded images
            for filename, file_data in uploaded_files:
                safe_fname = os.path.basename(filename)
                dest = IMAGES_DIR / f"{slug}_{safe_fname}"
                dest.write_bytes(file_data)
                work["images"].append(f"local://images/works/{slug}_{safe_fname}")

            save_works(cat_key, works)
            action = "Zapisano" if is_edit else "Dodano"
            self.send_redirect(f"/admin/category/{cat_key}?msg={action}: {title}")
            return

        self.send_redirect("/admin")


def main():
    port = 5000
    print(f"""
╔══════════════════════════════════════════════╗
║  CMS — Izabela Chamczyk                     ║
║  Otwórz w przeglądarce: http://localhost:{port} ║
║  Aby zakończyć: Ctrl+C                      ║
╚══════════════════════════════════════════════╝
""")
    server = HTTPServer(("localhost", port), CMSHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
        server.server_close()


if __name__ == "__main__":
    main()
