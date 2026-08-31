#!/usr/bin/env python3
"""
build_site.py - JSON → HTML generator for Nagy Botond Cycling Website
Reads data/content.json and replaces SECTION markers in index.html
Also auto-discovers gallery images from Pictures/ folder
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(SCRIPT_DIR, 'index.html')
JSON_PATH = os.path.join(SCRIPT_DIR, 'data', 'content.json')
PICTURES_DIR = os.path.join(SCRIPT_DIR, 'Pictures')
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, 'template.html')
UI_STRINGS_PATH = os.path.join(SCRIPT_DIR, 'data', 'ui-strings.json')
BASE_URL = 'https://botondnagy.eu'

LANGUAGES = ['hu', 'en', 'de', 'sl']
DEFAULT_LANG = 'hu'


def load_ui_strings():
    with open(UI_STRINGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def tr(field, lang):
    """Return the lang-specific value of a translatable field.
    Falls back to DEFAULT_LANG if the field is a dict but lacks `lang`.
    Non-dict fields (icons, paths, colors, proper nouns) are returned as-is.
    """
    if isinstance(field, dict) and set(field.keys()) <= {'hu', 'en', 'de', 'sl'}:
        return field.get(lang) or field.get(DEFAULT_LANG, '')
    return field


def _is_leaf_translation(value):
    """True for a {'hu':..,'en':..,'de':..,'sl':..} leaf whose values are the
    actual translated strings (as opposed to e.g. languageSwitcher, whose
    top-level keys are also hu/en/de/sl but whose values are nested dicts)."""
    return (
        isinstance(value, dict)
        and set(value.keys()) <= {'hu', 'en', 'de', 'sl'}
        and all(isinstance(v, str) for v in value.values())
    )


def flatten_ui_strings(ui_strings, lang, prefix=''):
    """Flatten nested ui-strings dict into {'a.b.c': 'translated value'} for one lang."""
    flat = {}
    for key, value in ui_strings.items():
        full_key = f'{prefix}.{key}' if prefix else key
        if _is_leaf_translation(value):
            flat[full_key] = value.get(lang) or value.get(DEFAULT_LANG, '')
        elif isinstance(value, dict):
            flat.update(flatten_ui_strings(value, lang, full_key))
    return flat


def apply_ui_strings(html, lang, ui_strings):
    flat = flatten_ui_strings(ui_strings, lang)
    for key, value in flat.items():
        html = html.replace('{{i18n:' + key + '}}', value)
    return html


def lang_url(lang):
    return f'{BASE_URL}/' if lang == DEFAULT_LANG else f'{BASE_URL}/{lang}/'


def build_hreflang_tags():
    lines = []
    for lang in LANGUAGES:
        lines.append(f'    <link rel="alternate" hreflang="{lang}" href="{lang_url(lang)}">')
    lines.append(f'    <link rel="alternate" hreflang="x-default" href="{lang_url(DEFAULT_LANG)}">')
    return '\n'.join(lines)


def build_language_switcher(current_lang, ui_strings):
    labels = {l: ui_strings['languageSwitcher'][l][l] for l in LANGUAGES}
    flags = {'hu': '🇭🇺', 'en': '🇬🇧', 'de': '🇩🇪', 'sl': '🇸🇮'}
    items = []
    for lang in LANGUAGES:
        active = ' text-neon-blue' if lang == current_lang else ' text-gray-400'
        items.append(
            f'<a href="{lang_url(lang)}" class="text-xs font-mono tracking-wider hover:text-neon-blue '
            f'transition-colors{active}">{flags[lang]} {labels[lang]}</a>'
        )
    return (
        '<div class="flex items-center gap-3 ml-4 pl-4 border-l border-white/10">'
        + ''.join(items) + '</div>'
    )


def load_json():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def discover_images():
    """Auto-discover images from Pictures/ folder (top-level files only)"""
    if not os.path.isdir(PICTURES_DIR):
        return []
    exts = {'.jpg', '.jpeg', '.png', '.webp'}
    images = []
    for fname in sorted(os.listdir(PICTURES_DIR)):
        fpath = os.path.join(PICTURES_DIR, fname)
        if os.path.isfile(fpath) and os.path.splitext(fname)[1].lower() in exts:
            images.append(fname)
    return images


def get_optimized_path(original_path, size, fmt):
    """Convert 'Pictures/IMG_1952.jpeg' to optimized path.
    size: 'thumb' or 'medium'
    fmt: 'jpeg' or 'webp'
    """
    fname = os.path.basename(original_path)
    stem = os.path.splitext(fname)[0]
    if fmt == 'webp':
        return f'Pictures/optimized/{size}-webp/{stem}.webp'
    else:
        return f'Pictures/optimized/{size}/{stem}.jpeg'


def picture_element(original_path, size, alt, extra_attrs='', indent=20, data_full=False):
    """Generate a <picture> element with WebP source and JPEG fallback.
    size: 'thumb' or 'medium'
    data_full: if True, adds data-full-jpeg attr pointing to medium version (for lightbox)
    """
    pad = ' ' * indent
    webp_src = get_optimized_path(original_path, size, 'webp')
    jpeg_src = get_optimized_path(original_path, size, 'jpeg')

    data_attr = ''
    if data_full:
        medium_jpeg = get_optimized_path(original_path, 'medium', 'jpeg')
        data_attr = f' data-full-jpeg="{medium_jpeg}"'

    extra = f' {extra_attrs}' if extra_attrs else ''
    return (
        f'{pad}<picture>\n'
        f'{pad}    <source srcset="{webp_src}" type="image/webp">\n'
        f'{pad}    <img src="{jpeg_src}" alt="{alt}"{extra}{data_attr}>\n'
        f'{pad}</picture>'
    )


def build_hero(data, lang):
    hero = data['hero']
    return f'''            <!-- Fő név -->
            <h1 class="hero-content font-orbitron text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-black tracking-tight leading-none mb-4 neon-text neon-glow-pulse text-white">
                {hero['name']}
            </h1>

            <!-- Alcím - typewriter effekt -->
            <div class="hero-content-delay mb-8 h-8 flex items-center justify-center">
                <span id="typewriter-text" class="typewriter font-mono text-sm sm:text-base md:text-lg text-gray-300 tracking-wider">
                    {tr(hero['subtitle'], lang)}
                </span>
            </div>

            <!-- Csapat badge -->
            <div class="hero-content-delay">
                <span class="inline-flex items-center gap-2 bg-neon-blue/10 border border-neon-blue/30 px-5 py-2 rounded-full text-neon-blue font-mono text-xs tracking-wider">
                    <span class="w-2 h-2 bg-neon-green rounded-full animate-pulse"></span>
                    {hero['team']}
                </span>
            </div>

            <!-- Fő fotó -->
            <div class="hero-content-delay mt-10 mx-auto max-w-md">
                <div class="hero-image aspect-[3/4] max-h-[420px] mx-auto shadow-2xl shadow-neon-blue/10">
{picture_element(hero['heroImage'], 'medium', f"{hero['name']} verseny közben", 'loading="eager"', indent=20)}
                </div>
            </div>'''


def build_stats(data, lang):
    stats = data['stats']
    cards = []
    for i, stat in enumerate(stats):
        delay = (i + 1) * 0.1
        color_class = {
            'blue': 'text-neon-blue neon-text',
            'green': 'text-neon-green neon-text-green',
            'white': 'text-white'
        }.get(stat.get('color', 'white'), 'text-white')

        data_count = f' data-count="{stat["dataCount"]}"' if 'dataCount' in stat else ''
        size_class = 'text-4xl sm:text-5xl' if 'dataCount' in stat else 'text-xl sm:text-2xl'

        cards.append(f'''                <div class="glass-card p-5 sm:p-7 text-center reveal" style="transition-delay: {delay}s">
                    <div class="text-2xl mb-2">{stat['icon']}</div>
                    <div class="text-xs font-mono text-gray-400 tracking-wider uppercase mb-2">{tr(stat['label'], lang)}</div>
                    <div class="stat-value {size_class} font-bold {color_class}"{data_count}>{tr(stat['value'], lang)}</div>
                </div>''')

    return '''            <!-- Stats kártyák grid -->
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
''' + '\n\n'.join(cards) + '''
            </div>'''


def build_achievements(data, lang):
    ach = data['achievements']
    parts = []

    # Intro text
    parts.append(f'''            <!-- Megjegyzés -->
            <div class="text-center mb-12 reveal">
                <p class="text-gray-400 text-sm font-body max-w-2xl mx-auto">
                    {tr(ach['intro'], lang)}
                </p>
            </div>''')

    for ci, cat in enumerate(ach['categories']):
        is_last_cat = (ci == len(ach['categories']) - 1)
        mb = 'mb-16' if not is_last_cat else ''
        cat_name = tr(cat['name'], lang)

        parts.append(f'''
            <!-- ===== {cat_name.upper()} EREDMÉNYEK ===== -->
            <div class="{mb}">
                <div class="flex items-center gap-3 mb-8 reveal">
                    <span class="text-2xl">{cat['icon']}</span>
                    <h3 class="font-orbitron text-xl sm:text-2xl font-bold text-white">{cat_name}</h3>
                </div>

                <div class="relative">
                    <div class="timeline-line hidden md:block"></div>
                    <div class="timeline-line md:hidden" style="left: 20px;"></div>''')

        for ri, result in enumerate(cat['results']):
            is_last = (ri == len(cat['results']) - 1)
            side = 'left' if ri % 2 == 0 else 'right'
            mb_class = '' if is_last else ' mb-12 md:mb-16'
            border_style = ' style="border-color: rgba(57, 255, 20, 0.3);"' if result.get('highlight') else ''

            # Build card inner content
            inner_lines = []
            inner_lines.append(f'                                <div class="font-mono text-xs text-neon-green tracking-wider mb-1">{tr(result["ageGroup"], lang)}</div>')
            inner_lines.append(f'                                <h3 class="font-orbitron text-base sm:text-lg font-bold text-white mb-1">{result["title"]}</h3>')

            desc = tr(result.get('description', ''), lang)
            if desc and 'subResults' not in result:
                inner_lines.append(f'                                <p class="text-gray-400 text-xs mb-2">{desc}</p>')

            if 'subResults' in result:
                if desc:
                    inner_lines.append(f'                                <p class="text-gray-400 text-xs mb-3">{desc}</p>')
                inner_lines.append('                                <div class="space-y-2">')
                for sub in result['subResults']:
                    justify = ' md:justify-end' if side == 'left' else ''
                    sub_event = tr(sub['event'], lang)
                    sub_place = tr(sub['place'], lang)
                    if sub.get('isTotal'):
                        color = sub.get('totalColor', 'text-neon-blue')
                        inner_lines.append(f'                                    <div class="flex items-center gap-2 text-sm border-t border-white/10 pt-2 mt-2{justify}">')
                        inner_lines.append(f'                                        <span>{sub["medal"]}</span>')
                        inner_lines.append(f'                                        <span class="{color} font-bold">{sub_event} – {sub_place}</span>')
                        inner_lines.append(f'                                    </div>')
                    else:
                        inner_lines.append(f'                                    <div class="flex items-center gap-2 text-sm{justify}">')
                        inner_lines.append(f'                                        <span>{sub["medal"]}</span>')
                        inner_lines.append(f'                                        <span class="text-gray-300"><span class="text-white font-medium">{sub_event}</span> – {sub_place}</span>')
                        inner_lines.append(f'                                    </div>')
                inner_lines.append('                                </div>')
            else:
                justify = ' md:justify-end' if side == 'left' else ''
                place_color = result.get('placeColor', 'text-gray-300')
                inner_lines.append(f'                                <div class="flex items-center gap-2{justify}">')
                inner_lines.append(f'                                    <span class="text-2xl">{result["medal"]}</span>')
                inner_lines.append(f'                                    <span class="{place_color} font-bold">{tr(result["place"], lang)}</span>')
                inner_lines.append(f'                                </div>')

            inner_html = '\n'.join(inner_lines)

            # Build timeline item
            if side == 'left':
                parts.append(f'''
                    <div class="relative flex flex-col md:flex-row md:items-center{mb_class} reveal">
                        <div class="timeline-dot hidden md:block" style="top: 50%;"></div>
                        <div class="timeline-dot md:hidden" style="top: 24px; left: 20px;"></div>
                        <div class="md:w-1/2 md:pr-12 md:text-right pl-12 md:pl-0">
                            <div class="glass-card p-5 sm:p-6 neon-border"{border_style}>
{inner_html}
                            </div>
                        </div>
                        <div class="md:w-1/2 hidden md:block"></div>
                    </div>''')
            else:
                parts.append(f'''
                    <div class="relative flex flex-col md:flex-row md:items-center{mb_class} reveal">
                        <div class="timeline-dot hidden md:block" style="top: 50%;"></div>
                        <div class="timeline-dot md:hidden" style="top: 24px; left: 20px;"></div>
                        <div class="md:w-1/2 hidden md:block"></div>
                        <div class="md:w-1/2 md:pl-12 pl-12">
                            <div class="glass-card p-5 sm:p-6 neon-border"{border_style}>
{inner_html}
                            </div>
                        </div>
                    </div>''')

        parts.append('''                </div>
            </div>''')

    return '\n'.join(parts)


def build_gallery(images, lang, ui_strings):
    """Build gallery HTML from image list"""
    if not images:
        empty_text = ui_strings['gallery']['empty'].get(lang) or ui_strings['gallery']['empty']['hu']
        return f'            <p class="text-gray-400 text-center">{empty_text}</p>'

    grid_images = images[:5]
    rest_images = images[5:]

    lines = ['            <div class="photo-grid reveal">']
    for fname in grid_images:
        lines.append(f'                <div class="gallery-img">')
        lines.append(picture_element(f'Pictures/{fname}', 'thumb', 'Nagy Botond', 'loading="lazy"', indent=20, data_full=True))
        lines.append(f'                </div>')
    lines.append('            </div>')

    if rest_images:
        lines.append('            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 reveal" style="transition-delay: 0.2s;">')
        for fname in rest_images:
            lines.append(f'                <div class="gallery-img h-48 sm:h-56">')
            lines.append(picture_element(f'Pictures/{fname}', 'thumb', 'Nagy Botond', 'loading="lazy"', indent=20, data_full=True))
            lines.append(f'                </div>')
        lines.append('            </div>')

    return '\n'.join(lines)


def build_bike(data, lang):
    bike = data['bike']
    spec_lines = []
    for i, spec in enumerate(bike['specs']):
        is_last = (i == len(bike['specs']) - 1)
        border = ' border-b border-white/5' if not is_last else ''
        color = 'text-neon-blue font-medium' if spec['label'] == 'Szín' else 'text-white font-medium'
        spec_lines.append(f'''                        <div class="flex justify-between items-center py-2{border}">
                            <span class="font-mono text-xs text-gray-400 uppercase tracking-wider">{tr(spec['label'], lang)}</span>
                            <span class="{color}">{spec['value']}</span>
                        </div>''')

    specs_html = '\n'.join(spec_lines)
    bike_name = tr(bike['name'], lang)

    return f'''            <div class="max-w-lg mx-auto">
                <!-- {bike_name} -->
                <div class="glass-card p-6 sm:p-8 neon-border reveal-left">
                    <!-- Animált kerék SVG -->
                    <div class="flex items-center justify-between mb-6">
                        <h3 class="font-orbitron text-xl sm:text-2xl font-bold text-white">{bike_name}</h3>
                        <svg width="48" height="48" viewBox="0 0 48 48" class="wheel-spin">
                            <circle cx="24" cy="24" r="20" stroke="#00D4FF" stroke-width="2" fill="none"/>
                            <circle cx="24" cy="24" r="16" stroke="#00D4FF" stroke-width="0.5" fill="none" opacity="0.3"/>
                            <circle cx="24" cy="24" r="3" fill="#00D4FF"/>
                            <line x1="24" y1="4" x2="24" y2="44" stroke="#00D4FF" stroke-width="0.5" opacity="0.4"/>
                            <line x1="4" y1="24" x2="44" y2="24" stroke="#00D4FF" stroke-width="0.5" opacity="0.4"/>
                            <line x1="9.86" y1="9.86" x2="38.14" y2="38.14" stroke="#00D4FF" stroke-width="0.5" opacity="0.4"/>
                            <line x1="38.14" y1="9.86" x2="9.86" y2="38.14" stroke="#00D4FF" stroke-width="0.5" opacity="0.4"/>
                        </svg>
                    </div>

                    <!-- Kép -->
                    <div class="gallery-img h-48 mb-6">
{picture_element(bike['image'], 'medium', 'Botond országúti kerékpárja', 'loading="lazy"', indent=24)}
                    </div>

                    <div class="space-y-3">
{specs_html}
                    </div>
                </div>

            </div>'''


def build_motivation(data, lang):
    mot = data['motivation']

    cards_lines = []
    for i, card in enumerate(mot['cards']):
        delay = (i + 1) * 0.1
        cards_lines.append(f'''                <div class="glass-card p-5 text-center reveal" style="transition-delay: {delay}s">
                    <div class="text-3xl mb-3">{card['icon']}</div>
                    <p class="text-gray-300 text-sm leading-relaxed">{tr(card['text'], lang)}</p>
                </div>''')

    cards_html = '\n'.join(cards_lines)

    photos_lines = []
    for photo in mot.get('photos', []):
        photos_lines.append(f'''                <div class="gallery-img h-48 sm:h-64">
{picture_element(photo, 'medium', 'Nagy Botond', 'loading="lazy"', indent=20)}
                </div>''')

    photos_html = '\n'.join(photos_lines)

    return f'''            <!-- Fő idézet -->
            <div class="text-center mb-12 reveal">
                <svg class="w-8 h-8 mx-auto mb-4 text-neon-blue/30" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10H14.017zM0 21v-7.391c0-5.704 3.731-9.57 8.983-10.609L9.978 5.151c-2.432.917-3.995 3.638-3.995 5.849h4v10H0z"/>
                </svg>
                <blockquote class="font-orbitron text-2xl sm:text-3xl md:text-4xl font-bold text-white leading-relaxed italic">
                    {tr(mot['quote'], lang)}
                </blockquote>
            </div>

            <!-- Motivációs kártyák -->
            <div class="grid sm:grid-cols-3 gap-4 sm:gap-6">
{cards_html}
            </div>

            <!-- Extra fotók -->
            <div class="grid grid-cols-2 gap-4 mt-10 reveal" style="transition-delay: 0.3s;">
{photos_html}
            </div>'''


def build_footer(data, lang):
    footer = data['footer']

    social_lines = []
    for link in footer.get('socialLinks', []):
        if link['platform'] == 'instagram':
            social_lines.append(f'''                <a href="{link['url']}" class="group" aria-label="Instagram">
                    <div class="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center group-hover:border-neon-blue/50 group-hover:bg-neon-blue/10 transition-all duration-300">
                        <svg class="w-5 h-5 text-gray-400 group-hover:text-neon-blue transition-colors" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
                        </svg>
                    </div>
                </a>''')
        elif link['platform'] == 'strava':
            social_lines.append(f'''                <a href="{link['url']}" class="group" aria-label="Strava">
                    <div class="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center group-hover:border-neon-green/50 group-hover:bg-neon-green/10 transition-all duration-300">
                        <svg class="w-5 h-5 text-gray-400 group-hover:text-neon-green transition-colors" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169"/>
                        </svg>
                    </div>
                </a>''')

    social_html = '\n'.join(social_lines)

    return f'''            <!-- Logo -->
            <div class="mb-6">
                <img src="logos/nb-logo-primary-dark.svg" alt="NB Logo" class="h-[88px] mx-auto">
            </div>

            <!-- Social linkek -->
            <div class="flex items-center justify-center gap-6 mb-8">
{social_html}
            </div>

            <!-- Easter egg szöveg - kattintásra konfetti -->
            <p class="text-gray-500 text-sm font-mono cursor-pointer hover:text-gray-300 transition-colors" id="footer-easter-egg" role="button" tabindex="0" aria-label="Kattints a meglepetésért">
                {tr(footer['madeWith'], lang)}
            </p>
            <p class="text-gray-600 text-xs font-mono mt-2">
                &copy; {tr(footer['copyright'], lang)}
            </p>'''


def replace_sections(html, data, images, lang, ui_strings):
    """Replace all SECTION-START/SECTION-END blocks"""

    builders = {
        'hero': lambda: build_hero(data, lang),
        'stats': lambda: build_stats(data, lang),
        'achievements': lambda: build_achievements(data, lang),
        'gallery': lambda: build_gallery(images, lang, ui_strings),
        'bike': lambda: build_bike(data, lang),
        'motivation': lambda: build_motivation(data, lang),
        'footer': lambda: build_footer(data, lang),
    }

    for section_name, builder in builders.items():
        pattern = re.compile(
            r'(<!-- SECTION-START:' + re.escape(section_name) + r' -->)\n.*?\n(\s*<!-- SECTION-END:' + re.escape(section_name) + r' -->)',
            re.DOTALL
        )
        match = pattern.search(html)
        if match:
            new_content = builder()
            html = pattern.sub(
                lambda m: m.group(1) + '\n' + new_content + '\n' + m.group(2),
                html
            )
            print(f'  ✅ {section_name} section replaced')
        else:
            print(f'  ⚠️  {section_name} section markers not found - skipping')

    return html


def main():
    print('🔧 Building multilingual site from JSON...')

    if not os.path.exists(JSON_PATH):
        print(f'  ❌ Error: {JSON_PATH} not found!')
        sys.exit(1)
    if not os.path.exists(TEMPLATE_PATH):
        print(f'  ❌ Error: {TEMPLATE_PATH} not found!')
        sys.exit(1)

    data = load_json()
    ui_strings = load_ui_strings()
    images = discover_images()
    print(f'  📸 Found {len(images)} images in Pictures/')

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_html = f.read()

    hreflang_tags = build_hreflang_tags()

    for lang in LANGUAGES:
        print(f'  🌐 Building [{lang}]...')
        html = template_html
        html = replace_sections(html, data, images, lang, ui_strings)
        html = html.replace('{{HREFLANG_TAGS}}', hreflang_tags)
        html = html.replace('{{CANONICAL_URL}}', lang_url(lang))
        html = html.replace('{{LANGUAGE_SWITCHER}}', build_language_switcher(lang, ui_strings))
        html = apply_ui_strings(html, lang, ui_strings)

        if lang == DEFAULT_LANG:
            out_path = INDEX_PATH
        else:
            out_dir = os.path.join(SCRIPT_DIR, lang)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, 'index.html')

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'    ✅ Wrote {os.path.relpath(out_path, SCRIPT_DIR)} ({len(html)} chars)')

    print('  ✅ Done!')


if __name__ == '__main__':
    main()
