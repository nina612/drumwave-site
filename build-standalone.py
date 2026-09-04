#!/usr/bin/env python3
"""Fold the whole site into one self-contained HTML file.

    python3 build-standalone.py            full quality, about 7MB
    python3 build-standalone.py --light    re-encoded, about a third the size

Reads index.html and writes drumwave-standalone.html with every asset inlined:
images and fonts as data URIs, GSAP inlined as script text. The result opens with
no network and no sibling files, so it survives being emailed or copied onto a
stick — at the cost of front-loading everything before the first paint.

The fonts are the part worth explaining. Left as a Google Fonts <link> the file
still opens, but offline it falls back to a system sans and the whole page looks
wrong — the kind of failure you don't see until someone else opens it. So the
faces are embedded, latin subsets only: that is 16 faces instead of 48, and about
490KB instead of some 1.5MB. There is no non-latin copy on the page.

--light re-encodes the photographs smaller and softer and writes
drumwave-standalone-light.html instead. Lightweight HTML previewers (mail
clients, chat file previews) tend to hang on 7MB of base64 in one document;
the light build opens in them. Use the full build for anything anyone judges
the photography on.

Downloaded fonts are cached in .build-cache/ so a rebuild needs no network.
"""

import base64
import mimetypes
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "index.html")
OUT = os.path.join(HERE, "drumwave-standalone.html")
OUT_LIGHT = os.path.join(HERE, "drumwave-standalone-light.html")
CACHE = os.path.join(HERE, ".build-cache")

# a real browser UA, or Google serves the older truetype format instead of woff2
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml", ".gif": "image/gif", ".webp": "image/webp"}

KEEP_SUBSETS = ("latin", "latin-ext")


def fetch(url, name):
    """Download once, then serve from .build-cache on later runs."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as r, open(path, "wb") as f:
            f.write(r.read())
    return open(path, "rb").read()


def inline_fonts(css_url):
    css = fetch(css_url, "fonts.css").decode()
    # the stylesheet is one @font-face per subset, each preceded by a /* subset */
    # comment; split on those and keep only the ones the page can actually render
    blocks = re.split(r"(?=/\* [a-z-]+ \*/)", css)
    kept = [b for b in blocks
            if re.match(r"/\* (%s) \*/" % "|".join(KEEP_SUBSETS), b.strip())]
    css = "".join(kept)
    for url in sorted(set(re.findall(r"(https://fonts\.gstatic\.com[^)]*\.woff2)", css))):
        blob = fetch(url, url.rsplit("/", 1)[-1])
        css = css.replace(url, "data:font/woff2;base64," + base64.b64encode(blob).decode())
    return css, len(kept)


def shrink(blob, ext, max_w=1400, quality=68):
    """Re-encode one photograph smaller. Returns (bytes, mime) — the original
    if Pillow is missing, or if squeezing it made it bigger."""
    try:
        import io
        from PIL import Image
    except ImportError:
        return blob, None
    try:
        im = Image.open(io.BytesIO(blob))
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        out = buf.getvalue()
        return (out, "image/jpeg") if len(out) < len(blob) else (blob, None)
    except Exception:
        return blob, None


def main():
    light = "--light" in sys.argv
    dest = OUT_LIGHT if light else OUT
    if not os.path.exists(SRC):
        sys.exit("index.html not found next to this script")
    html = open(SRC).read()
    before = len(html)

    # --- fonts: drop the <link>s, embed the faces in their place ---
    m = re.search(r'<link href="(https://fonts\.googleapis\.com[^"]*)" rel="stylesheet">', html)
    faces = 0
    if m:
        css, faces = inline_fonts(m.group(1))
        html = re.sub(r"\n?<link rel=\"preconnect\"[^>]*>", "", html)
        html = html.replace(
            m.group(0),
            "<style>/* Titillium Web + Open Sans, latin subsets, embedded so the "
            "file stands on its own with no network */\n" + css + "</style>")

    # --- scripts: inline the library source ---
    scripts = 0
    for tag, path in re.findall(r'(<script src="(assets/js/[^"]+)"></script>)', html):
        full = os.path.join(HERE, path)
        if os.path.exists(full):
            html = html.replace(tag, "<script>" + open(full).read() + "</script>")
            scripts += 1

    # --- images: every reference becomes a data URI ---
    refs = sorted(set(re.findall(r"assets/img/[A-Za-z0-9_./'\- ]+?\.(?:png|jpg|jpeg|svg|gif|webp)", html)))
    images, missing = 0, []
    for rel in refs:
        full = os.path.join(HERE, rel)
        if not os.path.exists(full):
            missing.append(rel)
            continue
        ext = os.path.splitext(rel)[1].lower()
        blob = open(full, "rb").read()
        mime = MIME.get(ext, mimetypes.guess_type(rel)[0] or "application/octet-stream")
        # SVGs are already tiny and vector; leave them alone
        if light and ext in (".jpg", ".jpeg", ".png"):
            blob, remime = shrink(blob, ext)
            mime = remime or mime
        uri = "data:%s;base64,%s" % (mime, base64.b64encode(blob).decode())
        html = html.replace(rel, uri)
        images += 1

    # --- refuse to ship a file that still reaches for the network ---
    external = [r for r in re.findall(r'(?:src|href)="([^"]+)"', html)
                if not r.startswith(("data:", "mailto:", "#"))]

    open(dest, "w").write(html)
    mb = os.path.getsize(dest) / 1048576
    print("inlined %d font faces, %d scripts, %d images" % (faces, scripts, images))
    print("index.html %.0f KB -> %s %.2f MB%s" % (
        before / 1024, os.path.basename(dest), mb, " (re-encoded)" if light else ""))
    if missing:
        print("MISSING (left as-is): " + ", ".join(missing))
    if external:
        print("STILL EXTERNAL: " + ", ".join(sorted(set(external))))
        sys.exit("not self-contained — fix the above and rebuild")
    print("self-contained: no external src or href remain")


if __name__ == "__main__":
    main()
