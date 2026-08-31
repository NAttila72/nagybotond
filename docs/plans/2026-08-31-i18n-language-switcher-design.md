# Többnyelvű oldal (nyelvválasztóval) — Design

Dátum: 2026-08-31

## Cél

A jelenleg csak magyar nyelvű `botondnagy.eu` oldal elérhetővé tétele angolul,
németül és szlovénül is, nyelvválasztóval, a meglévő JSON → build script →
GitHub Pages munkafolyamat megtartásával.

## Architektúra

### 1. Adatmodell — `data/content.json`

Minden fordítandó szövegmező objektummá alakul:

```json
"subtitle": {
  "hu": "🚴 Road & Track Cyclist | 11 éves | Hungary 🇭🇺",
  "en": "...",
  "de": "...",
  "sl": "..."
}
```

Nem fordítandó, plain string marad: képútvonalak, színkódok/CSS osztályok,
emoji ikonok, számok (pl. érem-számláló), tulajdonnevek (rider név, csapatnév,
kerékpár márka/modell: "Bianchi XR3 CV", "Celeste").

Versenynevek (pl. "Mátra Kör", "Diákolimpia Országúti Időfutam") minden
nyelven az eredeti (magyar) néven maradnak — mint a valódi versenyneveket
általában nem szokás lefordítani. A körülöttük lévő leíró szöveg, korosztály-
és helyezés-feliratok viszont fordítandók.

Ha egy mezőnél hiányzik egy nyelvi fordítás, a build script a `hu` értékre
esik vissza — soha nem törik el emiatt az oldal.

### 2. Statikus feliratok — új `data/ui-strings.json`

A jelenlegi `index.html` sablonban van content.json-on kívüli, közvetlenül
beégetett magyar szöveg is: navigáció, szekció eyebrow-címkék
("// EREDMÉNYEK"), szekciócímek ("RIDER STATS"), a "Speed Challenge"
minijáték szövegei, `<title>`/meta description, ARIA-label-ek. Ezeket egy
külön 4 nyelvű JSON-ba gyűjtjük, ugyanazzal a `{hu, en, de, sl}` struktúrával.

### 3. Build folyamat — `build_site.py`

A script a 4 nyelvi kódra ciklust fut, nyelvenként:

- kiválasztja a megfelelő fordítást minden content.json mezőből (fallback
  `hu`-ra, ha hiányzik)
- legenerálja a JSON-vezérelt szekciókat a meglévő SECTION-START/END
  marker-mechanizmussal
- helyettesíti az új UI-string token-eket a sablonban
- beállítja a `<html lang="...">`, canonical és hreflang `<link>` tageket
- kiírja az eredményt: `index.html` (hu, gyökér, alapértelmezett),
  `en/index.html`, `de/index.html`, `sl/index.html`

Kép-optimalizálás (`optimize_images.py`) változatlan — a képek nyelvek
között megosztottak. A `sitemap.xml` a 4 URL-lel és hreflang alternate-ekkel
bővül.

### 4. Nyelvválasztó UI

Kis zászlós/dropdown váltó a navigációban (🇭🇺 🇬🇧 🇩🇪 🇸🇮), minden generált
oldalon jelen van, a másik 3 nyelv gyökér URL-jére mutat (`/`, `/en/`,
`/de/`, `/sl/`), az aktuális nyelv kiemelve.

### 5. Admin felület — `admin.html`

A "Szövegek" és "Eredmények" szerkesztőkben minden fordítandó mező mellé
HU/EN/DE/SL nyelvi fül kerül, hogy a jövőbeli tartalmi frissítések (pl. új
eredmény, státuszhír) mind a 4 nyelven közvetlenül szerkeszthetők legyenek
AI segítség nélkül is. Mentéskor továbbra is egyetlen `data/content.json`
commitolódik a meglévő GitHub API mechanizmuson keresztül — az nem változik.

Az `ui-strings.json` (ritkán változó, statikus feliratok) NEM kerül be az
admin felületbe — azt közvetlenül JSON-ban tartjuk karban, hogy ne kelljen
az admin.html-t ezért is átalakítani.

### 6. Kezdeti fordítás

A jelenlegi teljes magyar tartalom lefordításra kerül angolra, németre és
szlovénre az implementáció részeként.

## Nem cél / kihagyva

- Böngésző nyelv-detektálás alapú automatikus átirányítás — a felhasználó
  kézzel választ nyelvet a switcherrel.
- Nyelvspecifikus URL-ösvények a gyökéren kívüli aloldalakhoz (nincs is
  aloldal, az oldal egy hosszú single-page).
