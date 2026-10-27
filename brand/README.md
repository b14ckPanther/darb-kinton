# Darb Kinton brand

Kinton is a Darb product. It wears Darb's colours (night, forest, gold, ivory) and has its own mark: **the flying nimbus as a cast-gold crest, with a keyhole through its heart that glows from inside.** In the show, Kinton (筋斗雲) only carries the pure of heart. In the app, only your own devices can open what you send: the server only ever sees ciphertext.

The hero image carries the same idea in flight: your file, closed with a gold seal struck with the crest, riding the nimbus across the night.

Chosen by Nour from four meaning-led directions (A "Only you can ride it" for the icon, C "Sealed in flight" for the hero; B "Straight there" and D "Drop it, it flies" are kept in `concepts/`).

## See it

```sh
cd brand && npm install
node scripts/serve.mjs          # http://127.0.0.1:4180/ : brand sheet with every asset
```

## Rebuild every asset

```sh
npm run build                   # renders the two masters in Blender Cycles, then cuts everything
RENDER=0 npm run build          # reuses masters/ (no Blender needed) and rebuilds the flat assets
BLENDER=/path/to/blender npm run build   # when blender is not on PATH
```

Nothing is drawn by hand and nothing is hardcoded in the build:

| File | Holds |
|---|---|
| `src/tokens.json` | colours and roles, type, the crest's geometry (puffs, spirals, keyhole, tails), render samples, icon sizes, copy |
| `src/crest.mjs` | the crest outlines, shared by the 3D render (as `src/crest.json`) and the flat SVG marks, so they always match |
| `src/render.py` | Blender scene: the crest cast in gold on a night lacquer medallion (`tile`), and the sealed file on volumetric vapour (`hero`) |
| `scripts/build.mjs` | renders the masters, cuts every icon, writes the SVG marks, wordmarks, social cards, manifest and CSS tokens |
| `masters/` | the two Blender renders, committed so the flat assets rebuild without Blender |
| `concepts/` | the four directions and `blender/kinton.py`, the script that rendered them |

## What's in `exports/`

| Path | Use |
|---|---|
| `icons/icon-192.png`, `icon-512.png` | PWA icons, purpose `any` (squircle cut) |
| `icons/icon-maskable-192.png`, `-512.png` | PWA maskable (medallion inside the 80% safe zone) |
| `icons/apple-touch-icon.png` | iOS home screen, 180 px, opaque |
| `icons/icon-desktop-1024.png` | Desktop: macOS grid, 824 px body with system shadow |
| `icons/favicon.ico`, `favicon.svg`, `favicon-16/32/48.png` | Browser tab: no ring, tails or spirals, and a bigger keyhole, so it reads at 16 px |
| `icons/badge-96.png` | Notification badge and Android monochrome icon |
| `svg/mark-on-night.svg` | The flat mark on its night tile, ring and lit keyhole |
| `svg/mark-gold.svg`, `mark-ivory.svg`, `mark-ink.svg` | The crest alone, for any background |
| `svg/wordmark-on-dark.svg`, `-on-light.svg` | Lockup: mark, Darb, Kinton, 筋斗雲 (text outlined, no font needed) |
| `social/og-image.png`, `social/hero.png` | 1200 x 630 sharing card and 2400 x 1260 README hero |
| `manifest.webmanifest`, `head.html`, `tokens.css` | Drop-in PWA manifest, `<head>` tags and CSS tokens |

## Rules

- The keyhole is always open and lit from inside: it means "only yours". Never draw the crest without it, and never put a lock, shield or padlock beside it.
- No cartoon clouds, rockets, cyberpunk neon or purple glows.
- Darb's doorway outline belongs to Darb itself; Kinton never uses it.
- Every visual is original and made in code. No official Dragon Ball art, logos, characters or audio.
- Fonts: Zen Antique (display), Geist (interface) and Yuji Boku (筋斗雲 only), all under the SIL Open Font License (`fonts/`).
