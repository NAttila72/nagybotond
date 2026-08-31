# Többnyelvű oldal (EN/DE/SL) nyelvválasztóval — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** A `botondnagy.eu` oldal elérhető legyen magyarul (`/`), angolul (`/en/`),
németül (`/de/`) és szlovénül (`/sl/`), nyelvválasztóval, a meglévő
JSON → `build_site.py` → GitHub Pages munkafolyamat megtartásával.

**Architecture:** `data/content.json` fordítható mezői `{hu,en,de,sl}` objektummá
alakulnak. Egy új `data/ui-strings.json` tartalmazza a sablonba égetett statikus
feliratokat (nav, minijáték, meta tagek). A jelenlegi önmagát felülíró
`index.html` helyett egy stabil `template.html` lesz a build forrása
(sosem íródik felül), amiből a build script nyelvenként generál egy-egy
kimeneti HTML-t: `index.html` (hu), `en/index.html`, `de/index.html`,
`sl/index.html`. Az admin.html a fordítható mezőkhöz nyelvi füleket kap.

**Tech Stack:** Python 3 (build_site.py), sima HTML/CSS/JS (template.html,
admin.html), JSON adatfájlok, GitHub Actions + GitHub Pages.

**Design doc:** [2026-08-31-i18n-language-switcher-design.md](2026-08-31-i18n-language-switcher-design.md)

---

## Miért kell `template.html`?

A jelenlegi `build_site.py` az `index.html`-t olvassa be forrásként ÉS oda
írja vissza az eredményt (SECTION-START/END markerek közötti tartalmat
cseréli). Ez működik, amíg egyetlen nyelv van, mert a markereken kívüli rész
(nav, minijáték szövegei) sosem változik.

Ha most 4 nyelvet akarunk generálni ugyanabból a sablonból, a sablon nem
mutálódhat az első (magyar) futás után — különben a második (angol) futás
már csak magyar szöveget találna forrásként. Ezért bevezetünk egy stabil,
soha nem felülírt `template.html` forrásfájlt (benne a statikus feliratok
`{{i18n:kulcs}}` token formában), és a build script **mindig ebből** olvas,
a kimeneteket pedig a nyelvenkénti fájlokba írja.

---

### Task 1: Feature branch létrehozása

**Files:** nincs fájlváltozás

**Step 1:** Hozz létre egy külön branch-et, hogy a main (és az élő oldal)
változatlan maradjon, amíg a funkció készül.

```bash
git checkout -b feature/i18n
```

**Step 2:** Ellenőrizd, hogy a branch aktív.

```bash
git branch --show-current
```

Expected: `feature/i18n`

---

### Task 2: `template.html` létrehozása a jelenlegi `index.html`-ből

**Files:**
- Create: `template.html` (az `index.html` jelenlegi tartalmának másolata)

**Step 1:** Másold le a jelenlegi index.html-t template.html néven.

```bash
cp index.html template.html
```

**Step 2:** Commit.

```bash
git add template.html
git commit -m "Add template.html as stable build source for i18n"
```

Ezen a ponton még semmi nem használja a `template.html`-t — ez csak az
alap, amit a következő taskokban tokenizálunk.

---

### Task 3: Statikus feliratok tokenizálása a `template.html`-ben

**Files:**
- Modify: `template.html`

Cseréld le az alábbi, jelenleg beégetett magyar szövegeket `{{i18n:kulcs}}`
token-ekre a `template.html`-ben. A pontos kulcsneveket a Task 4-ben
definiált `ui-strings.json` struktúra adja.

**A `<head>`-ben (kb. 2-37. sor):**

| Jelenlegi | Csere |
|---|---|
| `<html lang="hu">` | `<html lang="{{i18n:htmlLang}}">` |
| `<meta name="description" content="...">` | `content="{{i18n:meta.description}}"` |
| `<link rel="canonical" href="https://botondnagy.eu/">` | `href="{{CANONICAL_URL}}"` |
| `<meta property="og:description" content="...">` | `content="{{i18n:meta.shareDescription}}"` |
| `<meta property="og:url" content="https://botondnagy.eu/">` | `content="{{CANONICAL_URL}}"` |
| `<meta property="og:locale" content="hu_HU">` | `content="{{i18n:ogLocale}}"` |
| `<meta name="twitter:description" content="...">` | `content="{{i18n:meta.shareDescription}}"` |

Közvetlenül a `<link rel="canonical">` sor után szúrd be az összes nyelvi
alternate linket egy token formájában (ezt a build script tölti ki, mert
csak ő ismeri az összes nyelv URL-jét egyszerre):

```html
{{HREFLANG_TAGS}}
```

**A navigációban (kb. 862-882. sor, desktop + mobile menü):**

| Jelenlegi | Csere |
|---|---|
| `Eredmények` (mindkét helyen) | `{{i18n:nav.achievements}}` |
| `Galéria` (mindkét helyen) | `{{i18n:nav.gallery}}` |
| `Felszerelés` (mindkét helyen) | `{{i18n:nav.equipment}}` |

(`Stats` és `Game` marad változatlan minden nyelven — már angol szavak.)

Közvetlenül a desktop nav lista után (a `#game` link után, még a `</div>`
előtt, kb. 866. sor után) szúrd be a nyelvválasztó helyét:

```html
{{LANGUAGE_SWITCHER}}
```

**ARIA labelek:**

| Jelenlegi | Csere |
|---|---|
| `aria-label="Menü megnyitása"` | `aria-label="{{i18n:aria.mobileMenu}}"` |
| `aria-label="Tovább görgetés"` | `aria-label="{{i18n:aria.scrollDown}}"` |
| `aria-label="Képnagyító"` | `aria-label="{{i18n:aria.lightboxDialog}}"` |
| `aria-label="Bezárás"` | `aria-label="{{i18n:aria.lightboxClose}}"` |
| `aria-label="Előző kép"` | `aria-label="{{i18n:aria.lightboxPrev}}"` |
| `aria-label="Következő kép"` | `aria-label="{{i18n:aria.lightboxNext}}"` |
| `aria-label="Kattints a játékhoz"` | `aria-label="{{i18n:aria.gameButton}}"` |
| `aria-label="Kattints a meglepetésért"` | `aria-label="{{i18n:aria.footerEasterEgg}}"` |

**Szekció eyebrow-k (a `// Xxx` feliratok, 4 helyen):**

| Jelenlegi | Csere |
|---|---|
| `// Statisztikák` | `{{i18n:sections.statsEyebrow}}` |
| `// Eredmények` | `{{i18n:sections.achievementsEyebrow}}` |
| `// Galéria` | `{{i18n:sections.galleryEyebrow}}` |
| `// Felszerelés` | `{{i18n:sections.equipmentEyebrow}}` |

(`// Fun Zone` marad változatlan.)

**Minijáték szövegei (kb. 1476-1516. sor):**

| Jelenlegi | Csere |
|---|---|
| `Kattints minél gyorsabban 10 másodpercig! Milyen gyors vagy?` | `{{i18n:game.instructions}}` |
| `Másodperc` | `{{i18n:game.secondsLabel}}` |
| `Kattintás` | `{{i18n:game.clicksLabel}}` |
| `Eredmény:` | `{{i18n:game.resultLabel}}` |
| `ÚJRA ↺` | `{{i18n:game.retryLabel}}` |

(A `START ⚡` gomb kezdőállapota marad, ld. alább a JS-ben.)

**Minijáték JS (kb. 1754-1816. sor) — a szkriptben lévő string literálok:**

| Jelenlegi JS literál | Csere |
|---|---|
| `'START ⚡'` (resetGame-ben) | `'{{i18n:game.startLabel}}'` |
| `'KATTINTS! 🔥'` | `'{{i18n:game.clickingLabel}}'` |
| `'VÉGE! 🏁'` | `'{{i18n:game.endLabel}}'` |
| `'🐌 Kezdő – Még gyakorolj!'` | `'{{i18n:game.rankBeginner}}'` |
| `'🚶 Amatőr – Nem rossz!'` | `'{{i18n:game.rankAmateur}}'` |
| `'🚴 Profi – Jó tempó!'` | `'{{i18n:game.rankPro}}'` |
| `'⚡ Bajnok – Szuper gyors!'` | `'{{i18n:game.rankChampion}}'` |
| `'🏆 LEGENDA – Hihetetlen! 🔥'` | `'{{i18n:game.rankLegend}}'` |

**Galéria üres állapot** — ez a `build_site.py`-ban van (nem a
template.html-ben), ld. Task 5.

**Step 1:** Végezd el a fenti cseréket a `template.html`-ben (kereséssel
könnyen megtalálhatók, a fájlban egyszer fordulnak elő).

**Step 2:** Ellenőrizd, hogy nem maradt véletlenül magyar szöveg a
markereken kívüli, statikus részeken.

```bash
grep -n "Eredmények\|Galéria\|Felszerelés\|Statisztikák\|Kattints\|Másodperc\|Kattintás\|Kezdő\|Amatőr\|Bajnok\|LEGENDA" template.html
```

Expected: csak a `{{i18n:...}}` tokenek maradnak, szó szerinti magyar
szöveg nem (a SECTION-START/END közötti, JSON-vezérelt részek kivételével,
azokat a Task 6 kezeli).

**Step 3:** Commit.

```bash
git add template.html
git commit -m "Tokenize static Hungarian strings in template.html for i18n"
```

---

### Task 4: `data/ui-strings.json` létrehozása

**Files:**
- Create: `data/ui-strings.json`

Hozd létre az alábbi struktúrát, minden kulcshoz hu/en/de/sl fordítással
(a hu oszlopot a jelenlegi, Task 3-ban kiszedett szövegek adják; az en/de/sl
fordítást természetes, a sportos-fiatalos hangnemhez illő stílusban készítsd
el — az emojik és a "//" prefix minden nyelven megmaradnak):

```json
{
  "htmlLang": {"hu": "hu", "en": "en", "de": "de", "sl": "sl"},
  "ogLocale": {"hu": "hu_HU", "en": "en_US", "de": "de_DE", "sl": "sl_SI"},
  "meta": {
    "description": {"hu": "...", "en": "...", "de": "...", "sl": "..."},
    "shareDescription": {"hu": "...", "en": "...", "de": "...", "sl": "..."}
  },
  "nav": {
    "achievements": {"hu": "Eredmények", "en": "...", "de": "...", "sl": "..."},
    "gallery": {"hu": "Galéria", "en": "...", "de": "...", "sl": "..."},
    "equipment": {"hu": "Felszerelés", "en": "...", "de": "...", "sl": "..."}
  },
  "aria": {
    "mobileMenu": {...}, "scrollDown": {...},
    "lightboxDialog": {...}, "lightboxClose": {...},
    "lightboxPrev": {...}, "lightboxNext": {...},
    "gameButton": {...}, "footerEasterEgg": {...}
  },
  "sections": {
    "statsEyebrow": {...}, "achievementsEyebrow": {...},
    "galleryEyebrow": {...}, "equipmentEyebrow": {...}
  },
  "gallery": {
    "empty": {"hu": "Nincs kép a galériában.", "en": "...", "de": "...", "sl": "..."}
  },
  "game": {
    "instructions": {...}, "secondsLabel": {...}, "clicksLabel": {...},
    "resultLabel": {...}, "startLabel": {...}, "clickingLabel": {...},
    "endLabel": {...}, "retryLabel": {...},
    "rankBeginner": {...}, "rankAmateur": {...}, "rankPro": {...},
    "rankChampion": {...}, "rankLegend": {...}
  },
  "languageSwitcher": {
    "hu": {"hu": "Magyar", "en": "Hungarian", "de": "Ungarisch", "sl": "Madžarščina"},
    "en": {"hu": "Angol", "en": "English", "de": "Englisch", "sl": "Angleščina"},
    "de": {"hu": "Német", "en": "German", "de": "Deutsch", "sl": "Nemščina"},
    "sl": {"hu": "Szlovén", "en": "Slovenian", "de": "Slowenisch", "sl": "Slovenščina"}
  }
}
```

(A `languageSwitcher` kulcsokat a Task 7-ben a nyelvválasztó UI-hoz
használjuk — minden nyelv neve az ÖSSZES nyelven elérhető, mert a
switcherben pl. az angol oldalon is látszik "Magyar", "Deutsch", stb. saját
magán a nyelvén szokás feltüntetni; ha inkább mindig a saját nyelvén
akarod feltüntetni mindegyiket ("Magyar", "English", "Deutsch",
"Slovenščina" — függetlenül attól, melyik oldalon vagyunk), akkor a
switcher HTML-jében egyszerűen mindig a `[lang][lang]` értéket használd,
ld. Task 7.)

**Step 1:** Hozd létre a fájlt a fenti struktúrával, kitöltve minden
fordítással.

**Step 2:** Validáld, hogy helyes JSON.

```bash
python3 -c "import json; json.load(open('data/ui-strings.json', encoding='utf-8')); print('OK')"
```

Expected: `OK`

**Step 3:** Commit.

```bash
git add data/ui-strings.json
git commit -m "Add ui-strings.json with HU/EN/DE/SL static UI translations"
```

---

### Task 5: `build_site.py` átalakítása többnyelvű generálásra

**Files:**
- Modify: `build_site.py`

**Step 1: Konstansok és helper függvények hozzáadása**

Add a fájl tetejéhez, a meglévő path-konstansok mellé:

```python
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


def flatten_ui_strings(ui_strings, lang, prefix=''):
    """Flatten nested ui-strings dict into {'a.b.c': 'translated value'} for one lang."""
    flat = {}
    for key, value in ui_strings.items():
        full_key = f'{prefix}.{key}' if prefix else key
        if isinstance(value, dict) and set(value.keys()) <= {'hu', 'en', 'de', 'sl'}:
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
```

**Step 2: Meglévő `build_*` függvények módosítása, hogy nyelvet kapjanak**

Minden `build_hero`, `build_stats`, `build_achievements`, `build_gallery`,
`build_bike`, `build_motivation`, `build_footer` függvény szignatúráját
egészítsd ki egy `lang` paraméterrel (`def build_hero(data, lang):` stb.),
és minden helyen, ahol eddig közvetlenül `hero['subtitle']`-t stb. írtál ki,
csavard be `tr(...)`-be:

```python
{tr(hero['subtitle'], lang)}
```

Ugyanígy: `stat['label']`, `stat['value']`, `ach['intro']`, `cat['name']`,
`result['ageGroup']`, `result['description']`, `result['place']`,
`sub['event']`, `sub['place']`, `mot['quote']`, `card['text']`,
`bike['name']`, `spec['label']`, `footer['madeWith']`,
`footer['copyright']` — mindegyiket `tr(..., lang)`-be csomagolva.

(`hero['name']`, `hero['team']`, minden `icon`, `color`, `medal`, path és
a bike/spec konkrét terméknevek — pl. `spec['value']` amikor
`"Bianchi XR3 CV"` — VÁLTOZATLANOK maradnak, mert azok plain string mezők
a content.json-ban, nem dict-ek; a `tr()` ilyenkor csak visszaadja
önmagát.)

A `build_gallery(images)` függvénybe add hozzá a `lang` és `ui_strings`
paramétert, és az üres-galéria fallback szöveget cseréld:

```python
def build_gallery(images, lang, ui_strings):
    if not images:
        empty_text = ui_strings['gallery']['empty'].get(lang) or ui_strings['gallery']['empty']['hu']
        return f'            <p class="text-gray-400 text-center">{empty_text}</p>'
    ...
```

**Step 3: `replace_sections` frissítése, hogy nyelvet adjon tovább**

```python
def replace_sections(html, data, images, lang, ui_strings):
    builders = {
        'hero': lambda: build_hero(data, lang),
        'stats': lambda: build_stats(data, lang),
        'achievements': lambda: build_achievements(data, lang),
        'gallery': lambda: build_gallery(images, lang, ui_strings),
        'bike': lambda: build_bike(data, lang),
        'motivation': lambda: build_motivation(data, lang),
        'footer': lambda: build_footer(data, lang),
    }
    # ... (a ciklus törzse változatlan)
```

**Step 4: `main()` átírása többnyelvű ciklusra**

```python
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
```

**Step 5: Futtasd a buildet, és ellenőrizd, hogy nem maradt fel nem oldott
token.**

```bash
python3 build_site.py
grep -rl "{{" index.html en/index.html de/index.html sl/index.html
```

Expected az első parancsnál: mind a 4 nyelv "✅ Wrote ..." sorral fut le,
hiba nélkül. A `grep -rl "{{"` parancs Expected kimenete: **semmi** (üres
— ha bármelyik fájl neve kiíródik, az azt jelenti, hogy maradt egy be nem
töltött `{{...}}` token, amit meg kell találni és javítani).

**Step 6: Commit.**

```bash
git add build_site.py
git commit -m "Refactor build_site.py to generate hu/en/de/sl pages from template.html"
```

---

### Task 6: `data/content.json` migrálása és lefordítása

**Files:**
- Modify: `data/content.json`

Alakítsd át a fájlt úgy, hogy minden alábbi mező `{"hu": ..., "en": ...,
"de": ..., "sl": ...}` objektum legyen (a jelenlegi magyar szöveg kerül a
`"hu"` kulcs alá, a többit fordítsd le természetes, a jelenlegi energikus,
fiatalos hangvételhez illő stílusban):

- `hero.subtitle`
- `stats[*].label` (mind a 6: Érmek, Specializáció, Versenyez, Kedvenc táv,
  Erősség, Álom)
- `stats[2].value` ("2024 óta"), `stats[3].value` ("20 km hegy"),
  `stats[4].value` ("Hegymenet 🏔️"), `stats[5].value` ("🌈 & sárga trikó")
  — **`stats[1].value` ("Road & Track") marad plain string**, mert már
  nyelvfüggetlen.
- `achievements.intro`
- `achievements.categories[*].name` ("Országúti kerékpár", "Pályakerékpár")
- `achievements.categories[*].results[*].ageGroup` — **csak azoknál, ahol
  van benne magyar szó** (pl. `"U15 mezőny · U13 értékelés ⬆️⬆️"`); a
  puszta `"U11"` és `"U13 ⬆️"` marad plain string.
- `achievements.categories[*].results[*].description` (ahol nem üres)
- `achievements.categories[*].results[*].place` (pl. "3. hely" → "3rd
  place" / "3. Platz" / "3. mesto")
- `achievements.categories[*].results[*].subResults[*].event` — "Scratch"
  marad változatlan (nemzetközi pályakerékpár-szakkifejezés), de
  "Pontverseny" → "Points race" / "Punktefahren" / "Točkovna dirka",
  "Elimináció" → "Elimination" / "Ausscheidungsfahren" / "Izločanje",
  "Omnium összesített" → "Omnium overall" / "Omnium Gesamt" / "Omnium
  skupno" (a "Scratch" mezőt hagyd plain stringként, mert minden nyelven
  ugyanaz).
- `achievements.categories[*].results[*].subResults[*].place` (pl. "2.
  hely")
- **A `title` mezők (pl. "Mátra Kör", "Diákolimpia Országúti Időfutam",
  "Szlovák Kupa – Budapest") NEM változnak — maradnak plain string,
  eredeti néven minden nyelven**, mint a valódi versenyneveknél szokás.
- `motivation.quote`
- `motivation.cards[*].text` (mind a 3)
- `bike.name` ("Országúti gép")
- `bike.specs[*].label` ("Modell", "Váz", "Technológia", "Kerék", "Szín")
  — **a `bike.specs[*].value` mezők maradnak plain string** (Bianchi XR3
  CV, Full Carbon, Countervail (CV), 700c, Celeste — mind márka-/
  terméknevek).
- `footer.copyright` ("2026 Nagy Botond. Minden jog fenntartva.")
  — **`footer.madeWith` marad plain string** ("Made with ❤️ and 🚴" már
  angol).

**Step 1:** Végezd el a migrációt + fordítást a fenti lista alapján.

**Step 2:** Validáld a JSON-t.

```bash
python3 -c "import json; json.load(open('data/content.json', encoding='utf-8')); print('OK')"
```

Expected: `OK`

**Step 3:** Futtasd újra a buildet, és nézd át mind a 4 nyelvi kimenetet
böngészőben (ld. Task 8 részletesen).

```bash
python3 build_site.py
```

**Step 4:** Commit.

```bash
git add data/content.json
git commit -m "Translate content.json fields to hu/en/de/sl"
```

---

### Task 7: Nyelvválasztó UI véglegesítése

A `build_language_switcher()` (Task 5, Step 1) már legenerálja a HTML-t.
Ez a task a beillesztés helyének finomítására és mobil nézetre vonatkozik.

**Files:**
- Modify: `template.html` (mobil menü nyelvválasztó helye)

**Step 1:** A desktop nav mellett a mobil hamburger-menübe is szúrj be egy
`{{LANGUAGE_SWITCHER}}` tokent (a mobil link-lista után, kb. 882. sor
után), hogy mobilon is elérhető legyen a váltó. Mivel a build script
ugyanazt a HTML snippet-et helyettesíti be mindkét helyre, ez
automatikusan működik — csak a tokent kell egyszer még beszúrnod.

**Step 2:** Futtasd újra a buildet, nyisd meg mobil nézetben (resize 375×812)
és ellenőrizd, hogy a nyelvválasztó látható és használható.

```bash
python3 build_site.py
```

**Step 3:** Commit (ha volt módosítás a template.html-ben).

```bash
git add template.html
git commit -m "Add language switcher to mobile nav"
```

---

### Task 8: Teljes vizuális ellenőrzés mind a 4 nyelven

**Files:** nincs kódváltozás, csak verifikáció

**Step 1:** Nyisd meg helyben mind a 4 legenerált fájlt a Böngésző panelen
(`file:///.../index.html`, `file:///.../en/index.html`,
`file:///.../de/index.html`, `file:///.../sl/index.html`), és ellenőrizd:

- a fő szöveg (hero, achievements intro, motivation, footer) a megfelelő
  nyelven jelenik-e meg
- a nav és a minijáték felirataik lefordítva jelennek-e meg
- a nyelvválasztó minden oldalon ott van, és a másik 3 nyelvre mutat
- a minijáték JS-e (kattints, timer, rangsor szövegek) a megfelelő
  nyelven fut-e (indíts el egy játékot mind a 4 nyelven)
- nincs látható `{{...}}` maradék token sehol

**Step 2:** Nézd meg a page source-t (`view-source:` vagy a Böngésző
`read_page`/`get_page_text` eszközével), és keress rá `{{` előfordulásra —
ennek üresnek kell lennie.

**Step 3:** Ha mindent rendben találtál, nincs mit commitolni (ez egy
verifikációs lépés).

---

### Task 9: `sitemap.xml` frissítése

**Files:**
- Modify: `sitemap.xml`

**Step 1:** Bővítsd ki a fájlt mind a 4 URL-lel, `xhtml:link`
hreflang-alternate bejegyzésekkel mindegyiknél (ehhez kell az `xmlns:xhtml`
namespace):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://botondnagy.eu/</loc>
    <lastmod>2026-08-31</lastmod>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="hu" href="https://botondnagy.eu/"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://botondnagy.eu/en/"/>
    <xhtml:link rel="alternate" hreflang="de" href="https://botondnagy.eu/de/"/>
    <xhtml:link rel="alternate" hreflang="sl" href="https://botondnagy.eu/sl/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://botondnagy.eu/"/>
  </url>
  <url>
    <loc>https://botondnagy.eu/en/</loc>
    <lastmod>2026-08-31</lastmod>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="hu" href="https://botondnagy.eu/"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://botondnagy.eu/en/"/>
    <xhtml:link rel="alternate" hreflang="de" href="https://botondnagy.eu/de/"/>
    <xhtml:link rel="alternate" hreflang="sl" href="https://botondnagy.eu/sl/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://botondnagy.eu/"/>
  </url>
  <url>
    <loc>https://botondnagy.eu/de/</loc>
    <lastmod>2026-08-31</lastmod>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="hu" href="https://botondnagy.eu/"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://botondnagy.eu/en/"/>
    <xhtml:link rel="alternate" hreflang="de" href="https://botondnagy.eu/de/"/>
    <xhtml:link rel="alternate" hreflang="sl" href="https://botondnagy.eu/sl/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://botondnagy.eu/"/>
  </url>
  <url>
    <loc>https://botondnagy.eu/sl/</loc>
    <lastmod>2026-08-31</lastmod>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="hu" href="https://botondnagy.eu/"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://botondnagy.eu/en/"/>
    <xhtml:link rel="alternate" hreflang="de" href="https://botondnagy.eu/de/"/>
    <xhtml:link rel="alternate" hreflang="sl" href="https://botondnagy.eu/sl/"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://botondnagy.eu/"/>
  </url>
</urlset>
```

**Step 2:** Validáld XML jólformáltságát.

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('sitemap.xml'); print('OK')"
```

Expected: `OK`

**Step 3:** Commit.

```bash
git add sitemap.xml
git commit -m "Add hu/en/de/sl entries with hreflang alternates to sitemap.xml"
```

---

### Task 10: GitHub Actions workflow ellenőrzése (várhatóan nincs teendő)

**Files:** `.github/workflows/deploy.yml` (valószínűleg nem módosul)

A workflow már lefuttatja a `python3 build_site.py`-t, és a teljes
repo-gyökeret (`path: '.'`) tölti fel Pages-re — ez az új `en/`, `de/`,
`sl/` mappákat is automatikusan tartalmazni fogja, mivel a build script
azokat a gyökérben hozza létre.

**Step 1:** Nézd át a workflow fájlt, és igazold, hogy nincs benne semmi,
ami kizárná az új almappákat (pl. `.gitignore` vagy `exclude` szabály).

```bash
cat .gitignore
```

**Step 2:** Ha az `en/`, `de/`, `sl/` mappák nincsenek a `.gitignore`-ban,
nincs teendő. Ha véletlenül benne lennének (pl. egy túl general `*/`
szabály miatt), pontosítsd a `.gitignore`-t, hogy ne zárja ki őket.

---

### Task 11: `admin.html` — nyelvi fülek a fordítható mezőkhöz

**Files:**
- Modify: `admin.html` (a `renderStatsEditor`, `renderAchievementsEditor`,
  `renderTextsEditor`, `renderMotivationCards`, `renderBikeSpecs`
  függvények, kb. 692-800. sor)

Ez a legnagyobb egyedi task, mert az admin JS jelenleg feltételezi, hogy
minden szövegmező egyetlen string. Egy kis, újrahasználható komponenst kell
bevezetni.

**Step 1: Írj egy `renderTranslatableInput` helper függvényt**

Keresd meg, hol vannak a jelenlegi input-generáló helперek (pl.
`escHtml`, a fájl elején/közepén), és mellé vedd fel:

```javascript
const EDITOR_LANGS = ['hu', 'en', 'de', 'sl'];

function renderTranslatableInput(fieldPath, valueObj, opts = {}) {
    const tag = opts.textarea ? 'textarea' : 'input';
    const rows = opts.textarea ? ' rows="2"' : '';
    const type = opts.textarea ? '' : ' type="text"';
    const tabs = EDITOR_LANGS.map(lang => `
        <button type="button" class="lang-tab" data-lang="${lang}" data-field="${fieldPath}">${lang.toUpperCase()}</button>
    `).join('');
    const inputs = EDITOR_LANGS.map(lang => {
        const val = escHtml((valueObj && valueObj[lang]) || '');
        const hidden = lang === EDITOR_LANGS[0] ? '' : ' hidden';
        return `<${tag}${type}${rows} class="lang-input${hidden}" data-lang="${lang}" data-field="${fieldPath}">${val}</${tag}>`;
    }).join('');
    return `<div class="translatable-field" data-field="${fieldPath}">
        <div class="lang-tabs">${tabs}</div>
        ${inputs}
    </div>`;
}
```

Ez minden fordítható mezőnél egy kis HU/EN/DE/SL fültáblát rajzol, és
alattuk 4 (egyszerre csak 1 látható) beviteli mezőt.

**Step 2: Kattintás-kezelő a fülekhez**

Vedd fel az admin.html globális eseménykezelői közé (ahol a többi
`addEventListener` van):

```javascript
document.addEventListener('click', (e) => {
    const tab = e.target.closest('.lang-tab');
    if (!tab) return;
    const container = tab.closest('.translatable-field');
    const lang = tab.dataset.lang;
    container.querySelectorAll('.lang-tab').forEach(t => t.classList.toggle('active', t === tab));
    container.querySelectorAll('.lang-input').forEach(inp => {
        inp.classList.toggle('hidden', inp.dataset.lang !== lang);
    });
});
```

**Step 3: A meglévő rendereket cseréld `renderTranslatableInput`-ra**

Minden helyen, ahol eddig `<input value="${escHtml(stat.label)}">`-hoz
hasonlót generáltál egy fordítható mezőhöz (a Task 6 listája adja meg,
melyik mező fordítható: `stat.label`, `stat.value` a nem-plain esetekben,
`ach.intro`, `cat.name`, `result.ageGroup`/`description`/`place`,
`sub.event`/`sub.place`, `mot.quote`, `card.text`, `bike.name`,
`spec.label`, `footer.copyright`), cseréld le
`renderTranslatableInput(fieldPath, value)` hívásra.

**Step 4: Mentéskor az objektum összeállítása**

Ahol jelenleg a mentés (`collectFormData` vagy hasonló, ami a
`data/content.json`-t összeállítja PUT-hoz) egyetlen string értéket olvas
ki egy inputból, ott most be kell gyűjteni mind a 4 nyelvi input értékét
egy objektumba:

```javascript
function collectTranslatable(fieldPath) {
    const container = document.querySelector(`.translatable-field[data-field="${fieldPath}"]`);
    const result = {};
    container.querySelectorAll('.lang-input').forEach(inp => {
        result[inp.dataset.lang] = inp.value;
    });
    return result;
}
```

És ezt hívd meg minden fordítható mezőnél a jelenlegi
`el.value`/`el.textContent` kiolvasás helyett, mielőtt a `content.json`
objektumot összeállítod a GitHub API PUT híváshoz.

**Step 5: Kis CSS a fülekhez**

A `<style>` blokkba (vagy meglévő CSS fájlba) vedd fel:

```css
.lang-tabs { display: flex; gap: 4px; margin-bottom: 4px; }
.lang-tab { font-size: 11px; padding: 2px 8px; border-radius: 4px; border: 1px solid #333; background: transparent; color: #888; cursor: pointer; }
.lang-tab.active, .lang-tab:first-child { color: #00D4FF; border-color: #00D4FF; }
.lang-input.hidden { display: none; }
```

**Step 6:** Nyisd meg helyben az `admin.html`-t a Böngésző panelen, és
ellenőrizd (GitHub token nélkül is látszódnia kell a UI-nak, csak a
mentés nem fog működni token nélkül):

- minden korábban egy-mezős szövegnél megjelenik-e a HU/EN/DE/SL fülsor
- fülváltásra a megfelelő input jelenik-e meg
- a nem-fordítható mezők (pl. bike.specs value-jai, event title-ök)
  változatlanul egyszerű input maradnak

**Step 7:** Commit.

```bash
git add admin.html
git commit -m "Add HU/EN/DE/SL language tabs to translatable fields in admin.html"
```

---

### Task 12: Végső regressziós ellenőrzés és branch összefoglaló

**Files:** nincs kódváltozás

**Step 1:** Futtasd újra a teljes build-et tiszta állapotból, és nézd át a
git diffet, hogy semmi nem maradt félkész.

```bash
python3 build_site.py
git status --short
git diff --stat
```

**Step 2:** Nyisd meg mind a 4 nyelvi oldalt még egyszer végig (Task 8
checklistje szerint), és külön figyelj:

- a legutóbb hozzáadott 2026-os státuszmondat (achievements.intro
  második fele) helyesen jelenik-e meg mind a 4 nyelven
- a Google Analytics script és a JSON-LD structured data (`<script
  type="application/ld+json">`) nem sérült-e a token-cserék során

**Step 3:** Ha minden rendben, jelezd a felhasználónak, hogy a
`feature/i18n` branch készen áll összevonásra — a merge/push egy külön,
explicit jóváhagyást igénylő lépés (élő oldalra deployol).

---

## Végrehajtási lehetőségek

A terv elkészült: `docs/plans/2026-08-31-i18n-language-switcher.md`.

**1. Subagent-Driven (ebben a sessionben)** — minden taskhoz friss subagent,
review a taskok között, gyors iteráció.

**2. Külön session (Parallel Session)** — új session nyílik worktree-ben,
executing-plans skill-lel, checkpointokkal.
