// Builds every Darb Kinton brand asset from src/tokens.json and src/crest.mjs.
//   npm run build              renders the masters in Blender (on PATH, or BLENDER=/path), then cuts everything
//   RENDER=0 npm run build     reuses masters/ and only rebuilds the flat assets
import { execFileSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import opentype from 'opentype.js'
import pngToIco from 'png-to-ico'
import sharp from 'sharp'
import { bounds, cloud, crestShapes, keyhole, spiral, tails } from '../src/crest.mjs'

const ROOT = fileURLToPath(new URL('..', import.meta.url))
const OUT = `${ROOT}exports/`
const MASTERS = `${ROOT}masters/`
const T = JSON.parse(await readFile(`${ROOT}src/tokens.json`, 'utf8'))
const C = Object.fromEntries(Object.entries(T.color).map(([k, v]) => [k, v.hex]))
const K = T.crest
for (const d of ['icons', 'svg', 'social']) await mkdir(`${OUT}${d}`, { recursive: true })
await mkdir(MASTERS, { recursive: true })

const font = async (f) => opentype.parse((await readFile(`${ROOT}fonts/${f}`)).buffer)
const seal = await font(T.type.seal.file)
const display = await font(T.type.display.file)
const ui = await font(T.type.ui.file)

// ---------- 3D masters (Blender Cycles) ----------

await writeFile(`${ROOT}src/crest.json`, JSON.stringify(crestShapes(K)))
const tileMaster = `${MASTERS}tile.png`, heroMaster = `${MASTERS}hero.png`
if (process.env.RENDER !== '0' || !existsSync(tileMaster) || !existsSync(heroMaster)) {
  const blender = process.env.BLENDER || 'blender'
  const run = (variant, out, w, h, samples) => {
    console.log(`rendering ${variant} ${w}x${h} at ${samples} samples`)
    execFileSync(blender, ['-b', '-P', `${ROOT}src/render.py`, '--', variant, out, String(w), String(h), String(samples)], { stdio: ['ignore', 'ignore', 'inherit'] })
  }
  run('tile', tileMaster, 2048, 2048, T.render.samples.icon)
  run('hero', heroMaster, T.icons.hero[0], T.icons.hero[1], T.render.samples.hero)
}

// ---------- the flat marks: the same outlines as the cast crest ----------

const path = (polys, f) => polys.map((p) => 'M' + p.map(([x, y]) => `${f(x, y)[0].toFixed(2)} ${f(x, y)[1].toFixed(2)}`).join('L') + 'Z').join('')
/** Fits crest space into a 200 x 200 box: `width` is how wide the crest is drawn, centred on (100, 100). */
function fitter(polys, width) {
  const b = bounds(polys), k = width / (b.x1 - b.x0)
  const cx = (b.x0 + b.x1) / 2, cy = (b.y0 + b.y1) / 2
  return (x, y) => [100 + (x - cx) * k, 100 - (y - cy) * k]
}
const full = [cloud(K), ...K.spirals.map((s) => spiral(K, s)), keyhole(K)]
const allPolys = [...full, ...tails(K)]

/** The crest with tails: `fill` for the metal, `light` (or none) shows through the keyhole. */
function crestSvg({ width = 150, fill, light, simple = false }) {
  const body = simple ? [cloud(K), keyhole(K, 1.25)] : full
  const f = fitter(simple ? body : allPolys, width)
  const glow = light ? `<path d="${path([keyhole(K, simple ? 1.45 : K.keyhole.glow)], f)}" fill="${light}"/>` : ''
  const tail = simple ? '' : tails(K).map((t) => `<path d="${path([t], f)}" fill="${fill}"/>`).join('')
  return `${glow}<path d="${path(body, f)}" fill="${fill}" fill-rule="evenodd"/>${tail}`
}
const ring = (stroke, w = 3.5) => `<circle cx="100" cy="100" r="86" fill="none" stroke="${stroke}" stroke-width="${w}"/>`
const defs = `<linearGradient id="g" x1="40" y1="40" x2="160" y2="160" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="${C.goldLight}"/><stop offset=".42" stop-color="${C.gold}"/><stop offset="1" stop-color="${C.goldDeep}"/></linearGradient>
  <radialGradient id="l" cx="42%" cy="36%" r="72%"><stop offset="0" stop-color="${C.forest}"/><stop offset="1" stop-color="${C.night}"/></radialGradient>`
const svg = (body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs>${defs}</defs>${body}</svg>\n`
const tile = `<rect width="200" height="200" rx="44" fill="url(#l)"/>`

const svgs = {
  'mark-on-night.svg': svg(`${tile}${ring('url(#g)')}${crestSvg({ width: 132, fill: 'url(#g)', light: C.goldLight })}`),
  'mark-gold.svg': svg(crestSvg({ width: 184, fill: 'url(#g)' })),
  'mark-ivory.svg': svg(crestSvg({ width: 184, fill: C.ivory })),
  'mark-ink.svg': svg(crestSvg({ width: 184, fill: C.ink })),
  // small sizes: no ring, no tails, no spirals, a bigger keyhole, so it reads at 16 px
  'favicon.svg': svg(`<rect width="200" height="200" rx="44" fill="${C.night}"/>${crestSvg({ width: 172, fill: C.gold, light: C.goldLight, simple: true })}`),
  'badge-mono.svg': svg(crestSvg({ width: 184, fill: '#fff', simple: true })),
}
for (const [f, s] of Object.entries(svgs)) await writeFile(`${OUT}svg/${f}`, s)

// ---------- wordmark (text outlined: no font needed to display it) ----------

const outline = (f, text, x, y, size, fill) => f.getPath(text, x, y, size).toSVG(2).replace('<path ', `<path fill="${fill}" `)
function lockup(ink, sub, accent) {
  const NAME = 196, DARB = 50, JP = 40, GAP = 26
  const nameB = display.getPath(T.shortName, 0, 0, NAME).getBoundingBox()
  const darbB = ui.getPath('Darb', 0, 0, DARB).getBoundingBox()
  const jpB = seal.getPath(T.japanese, 0, 0, JP).getBoundingBox()
  const base = -(nameB.y1 - GAP + darbB.y1)
  const H = base + Math.max(nameB.y2, 0)
  const x0 = H + 60
  const jpX = x0 + (nameB.x2 - nameB.x1) + 36 - jpB.x1
  const W = jpX + jpB.x2 + 4
  const mark = svgs['mark-on-night.svg'].replace(/<\/?svg[^>]*>/g, '').replace('id="g"', 'id="wg"').replaceAll('url(#g)', 'url(#wg)').replace('id="l"', 'id="wl"').replaceAll('url(#l)', 'url(#wl)')
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -8 ${Math.ceil(W)} ${Math.ceil(H + 16)}">
  <g transform="scale(${H / 200})">${mark}</g>
  ${outline(ui, 'Darb', x0 + 6 - darbB.x1, base + nameB.y1 - GAP, DARB, sub)}
  ${outline(display, T.shortName, x0 - nameB.x1, base, NAME, ink)}
  ${outline(seal, T.japanese, jpX, base, JP, accent)}
</svg>
`
}
await writeFile(`${OUT}svg/wordmark-on-dark.svg`, lockup(C.ivory, C.muted, C.gold))
await writeFile(`${OUT}svg/wordmark-on-light.svg`, lockup(C.ink, '#6f6357', C.goldDeep))

// ---------- icon set: the cast medallion on the night tile ----------

/** iOS-style superellipse ("squircle"), n = 5. */
function squircle(size, fill = '#fff') {
  const r = size / 2, pts = []
  for (let i = 0; i < 360; i++) {
    const t = (i / 360) * Math.PI * 2, c = Math.cos(t), s = Math.sin(t)
    pts.push(`${(r + Math.sign(c) * Math.abs(c) ** 0.4 * r).toFixed(2)},${(r + Math.sign(s) * Math.abs(s) ** 0.4 * r).toFixed(2)}`)
  }
  return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><polygon points="${pts.join(' ')}" fill="${fill}"/></svg>`)
}
const backdrop = (size) => Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><defs>
  <radialGradient id="b" cx="50%" cy="42%" r="70%"><stop offset="0" stop-color="${C.forest}"/><stop offset="1" stop-color="${C.night}"/></radialGradient></defs>
  <rect width="${size}" height="${size}" fill="url(#b)"/></svg>`)
/** The medallion at `scale` of the frame, centred on the night backdrop. */
async function composed(size, scale) {
  const m = Math.round(size * scale), off = Math.round((size - m) / 2)
  const art = await sharp(tileMaster).resize(m, m, { kernel: 'lanczos3' }).png().toBuffer()
  return sharp(backdrop(size)).composite([{ input: art, left: off, top: off }]).png().toBuffer()
}
const S = T.render.markScale
const cut = async (buf, size) => sharp(buf).composite([{ input: squircle(size), blend: 'dest-in' }]).png()

for (const s of T.icons.tile) await (await cut(await composed(s, S.tile), s)).toFile(`${OUT}icons/icon-${s}.png`)
for (const s of T.icons.maskable) await sharp(await composed(s, S.maskable)).toFile(`${OUT}icons/icon-maskable-${s}.png`)
await sharp(await composed(T.icons.apple, S.apple)).flatten({ background: C.night }).toFile(`${OUT}icons/apple-touch-icon.png`)
{
  // macOS / desktop: 824 px squircle on a 1024 canvas with the system drop shadow
  const size = T.icons.mac, body = Math.round(size * 0.805), off = Math.round((size - body) / 2)
  const art = await (await cut(await composed(body, S.mac), body)).toBuffer()
  const shadow = await sharp({ create: { width: size, height: size, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite([{ input: squircle(body, 'rgba(0,0,0,0.55)'), left: off, top: off + Math.round(size * 0.012) }])
    .blur(size * 0.012).png().toBuffer()
  await sharp(shadow).composite([{ input: art, left: off, top: off }]).png().toFile(`${OUT}icons/icon-desktop-${size}.png`)
}
for (const s of T.icons.favicon) await sharp(Buffer.from(svgs['favicon.svg'])).resize(s, s).png().toFile(`${OUT}icons/favicon-${s}.png`)
await writeFile(`${OUT}icons/favicon.ico`, await pngToIco(T.icons.favicon.map((s) => `${OUT}icons/favicon-${s}.png`)))
await sharp(Buffer.from(svgs['badge-mono.svg'])).resize(T.icons.badge, T.icons.badge).png().toFile(`${OUT}icons/badge-${T.icons.badge}.png`)
await writeFile(`${OUT}icons/favicon.svg`, svgs['favicon.svg'])

// ---------- social: the hero render with the copy set on its quiet left side ----------

/** Wraps `text` to lines no wider than `max` at `size` in font `f`. */
function wrap(f, text, size, max) {
  const lines = [''], words = text.split(' ')
  for (const w of words) {
    const next = lines.at(-1) ? `${lines.at(-1)} ${w}` : w
    if (f.getAdvanceWidth(next, size) > max && lines.at(-1)) lines.push(w)
    else lines[lines.length - 1] = next
  }
  return lines
}
async function social(w, h, file) {
  const u = h / 630, x = 72 * u
  const shade = `<linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="${C.night}" stop-opacity=".85"/><stop offset=".55" stop-color="${C.night}" stop-opacity="0"/></linearGradient>`
  const nameSize = 112 * u, nameY = 300 * u
  const desc = wrap(ui, T.description, 22 * u, 540 * u)
  const copy = [
    outline(ui, 'Darb', x + 4 * u, 196 * u, 34 * u, C.muted),
    outline(display, T.shortName, x, nameY, nameSize, C.ivory),
    outline(seal, T.japanese, x + display.getAdvanceWidth(T.shortName, nameSize) + 22 * u, nameY, 34 * u, C.gold),
    outline(ui, T.tagline, x + 2 * u, 372 * u, 34 * u, C.gold),
    ...desc.map((l, i) => outline(ui, l, x + 2 * u, (428 + i * 32) * u, 22 * u, C.muted)),
  ].join('')
  const over = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs>${shade}</defs><rect width="${w}" height="${h}" fill="url(#s)"/>${copy}</svg>`)
  await sharp(heroMaster).resize(w, h, { kernel: 'lanczos3' }).composite([{ input: over }]).png().toFile(file)
}
await social(T.icons.og[0], T.icons.og[1], `${OUT}social/og-image.png`)
await social(T.icons.hero[0], T.icons.hero[1], `${OUT}social/hero.png`)

// ---------- manifest, tokens, head tags ----------

const manifest = {
  name: T.name,
  short_name: T.shortName,
  description: T.tagline,
  display: 'standalone',
  background_color: C.night,
  theme_color: C.night,
  icons: [
    ...T.icons.tile.map((s) => ({ src: `/icons/icon-${s}.png`, sizes: `${s}x${s}`, type: 'image/png', purpose: 'any' })),
    ...T.icons.maskable.map((s) => ({ src: `/icons/icon-maskable-${s}.png`, sizes: `${s}x${s}`, type: 'image/png', purpose: 'maskable' })),
    { src: `/icons/badge-${T.icons.badge}.png`, sizes: `${T.icons.badge}x${T.icons.badge}`, type: 'image/png', purpose: 'monochrome' },
  ],
}
await writeFile(`${OUT}manifest.webmanifest`, JSON.stringify(manifest, null, 2) + '\n')

await writeFile(`${OUT}tokens.css`, `/* Generated from src/tokens.json by scripts/build.mjs. Edit the JSON, not this file. */
:root {
${Object.entries(T.color).map(([k, v]) => `  --${k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())}: ${v.hex}; /* ${v.role} */`).join('\n')}
  --font-seal: '${T.type.seal.family}', 'Hiragino Mincho ProN', serif;
  --font-display: '${T.type.display.family}', 'Hiragino Mincho ProN', serif;
  --font-ui: '${T.type.ui.family}', system-ui, sans-serif;
}
`)

await writeFile(`${OUT}head.html`, `<link rel="icon" href="/icons/favicon.ico" sizes="48x48">
<link rel="icon" href="/icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="${C.night}">
<meta property="og:title" content="${T.name}">
<meta property="og:description" content="${T.tagline}">
<meta property="og:image" content="/social/og-image.png">
<meta name="twitter:card" content="summary_large_image">
`)
console.log('built', OUT)
