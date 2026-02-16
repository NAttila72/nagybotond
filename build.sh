#!/bin/bash
# ============================================
# GALÉRIA BUILDER - Nagy Botond Cycling Website
# ============================================
# Használat: bash build.sh
#
# Ez a script beolvassa a Pictures/ mappa összes képét
# és frissíti az index.html galéria szekciót.
# Ha új képet teszel a Pictures/ mappába, futtasd újra!
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python3 build_gallery.py
