// Finishes the Blender renders (a soft optical glow on highlights), cuts app icons and builds concepts/compare.png.
import sharp from 'sharp'

const OUT = new URL('../concepts/', import.meta.url).pathname
const ALL = ['keyhole', 'direct', 'sealed', 'arc']
const NAMES = { keyhole: 'A  Only You Can Ride It', direct: 'B  Straight There', sealed: 'C  Sealed in Flight', arc: 'D  Drop It, It Flies' }
const squircle = (size) => { const pts = []; for (let i = 0; i < 360; i++) { const t = i / 180 * Math.PI, c = Math.cos(t), s = Math.sin(t); pts.push(`${(size/2 + Math.sign(c) * Math.abs(c) ** 0.4 * size/2).toFixed(1)},${(size/2 + Math.sign(s) * Math.abs(s) ** 0.4 * size/2).toFixed(1)}`) } return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><polygon points="${pts.join(' ')}" fill="#fff"/></svg>`) }

const comps = []
for (const [i, d] of ALL.entries()) {
  const raw = `${OUT}${d}-full.png`
  const glow = await sharp(raw).linear(1.0, -170).blur(24).toBuffer()
  const done = await sharp(raw).composite([{ input: glow, blend: 'screen' }]).png().toBuffer()
  await sharp(done).toFile(`${OUT}${d}.png`)
  const icon = await sharp(done).resize(512, 512).composite([{ input: squircle(512), blend: 'dest-in' }]).png().toBuffer()
  await sharp(icon).toFile(`${OUT}icon-${d}.png`)
  comps.push({ input: await sharp(done).resize(420).toBuffer(), left: 30 + i * 450, top: 30 })
  comps.push({ input: await sharp(icon).resize(120).toBuffer(), left: 140 + i * 450, top: 480 })
  comps.push({ input: await sharp(icon).resize(48).toBuffer(), left: 290 + i * 450, top: 516 })
  comps.push({ input: Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="420" height="44"><text x="210" y="30" font-family="Georgia" font-size="26" fill="#FBF7EC" text-anchor="middle">${NAMES[d]}</text></svg>`), left: 30 + i * 450, top: 620 })
}
await sharp({ create: { width: 1830, height: 690, channels: 4, background: '#0a1410' } }).composite(comps).png().toFile(`${OUT}compare.png`)
console.log('ok')
