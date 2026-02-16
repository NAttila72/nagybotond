#!/usr/bin/env python3
"""
Galéria Builder - Nagy Botond Cycling Website

Beolvassa a Pictures/ mappa összes képét és frissíti
az index.html galéria szekciót automatikusan.

Használat: python3 build_gallery.py
"""

import os
import re
import sys

PICTURES_DIR = "Pictures"
HTML_FILE = "index.html"
FIRST_ROW_COUNT = 5  # Az első sorban ennyi kép lesz (photo-grid)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def find_images(directory):
    """Képfájlok keresése a megadott mappában."""
    images = []
    if not os.path.isdir(directory):
        return images

    for filename in sorted(os.listdir(directory)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            images.append(os.path.join(directory, filename))

    return images


def generate_gallery_html(images):
    """Galéria HTML generálása a képlistából."""
    if not images:
        return ""

    lines = []
    lines.append('            <!-- GALLERY-START (Ne szerkeszd kézzel! A build.sh generálja.) -->')

    # Első sor: photo-grid (max FIRST_ROW_COUNT kép)
    first_row = images[:FIRST_ROW_COUNT]
    rest = images[FIRST_ROW_COUNT:]

    lines.append('            <div class="photo-grid reveal">')
    for img in first_row:
        lines.append('                <div class="gallery-img">')
        lines.append(f'                    <img src="{img}" alt="Nagy Botond" loading="lazy">')
        lines.append('                </div>')
    lines.append('            </div>')

    # Második sor: grid (a maradék képek)
    if rest:
        lines.append('            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 reveal" style="transition-delay: 0.2s;">')
        for img in rest:
            lines.append('                <div class="gallery-img h-48 sm:h-56">')
            lines.append(f'                    <img src="{img}" alt="Nagy Botond" loading="lazy">')
            lines.append('                </div>')
        lines.append('            </div>')

    lines.append('            <!-- GALLERY-END -->')

    return "\n".join(lines)


def update_html(html_file, gallery_html):
    """Az index.html galéria szekciójának frissítése."""
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # GALLERY-START ... GALLERY-END blokk cseréje
    pattern = r" *<!-- GALLERY-START.*?<!-- GALLERY-END -->"
    new_content = re.sub(pattern, gallery_html, content, flags=re.DOTALL)

    if new_content == content:
        print("⚠️  Nem találtam GALLERY-START / GALLERY-END markereket az index.html-ben!")
        sys.exit(1)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    # Ellenőrzések
    if not os.path.isdir(PICTURES_DIR):
        print(f"❌ Hiba: Nincs '{PICTURES_DIR}' mappa!")
        sys.exit(1)

    if not os.path.isfile(HTML_FILE):
        print(f"❌ Hiba: Nincs '{HTML_FILE}' fájl!")
        sys.exit(1)

    # Képek keresése
    print(f"🔍 Képek keresése a {PICTURES_DIR}/ mappában...")
    images = find_images(PICTURES_DIR)

    if not images:
        print("⚠️  Nincs kép a mappában!")
        sys.exit(1)

    print(f"📸 {len(images)} kép találva.\n")

    # Galéria generálás
    gallery_html = generate_gallery_html(images)

    # HTML frissítés
    update_html(HTML_FILE, gallery_html)

    # Eredmény
    print(f"✅ Galéria frissítve! ({len(images)} kép)\n")
    print("Képek:")
    for img in images:
        print(f"   📷 {img}")
    print()
    print("🌐 Nyisd meg / frissítsd az index.html-t a böngészőben.")


if __name__ == "__main__":
    main()
