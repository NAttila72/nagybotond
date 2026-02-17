#!/bin/bash
# ============================================
# SITE BUILDER - Nagy Botond Cycling Website
# ============================================
# Használat: bash build.sh
#
# Ez a script beolvassa a data/content.json tartalmát
# és a Pictures/ mappa képeit, majd frissíti az index.html-t.
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

pip install Pillow 2>/dev/null || pip3 install Pillow 2>/dev/null
python3 optimize_images.py
python3 build_site.py
