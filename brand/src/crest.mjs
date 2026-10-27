// The Darb Kinton crest as flat outlines, shared by the Blender render (via src/crest.json) and the SVG marks,
// so the cast-gold icon and the flat marks are the same drawing.
// Units: crest space, y up, roughly -2.2..1.3 wide. Every number comes from tokens.crest.

const arc = (cx, cy, r, a0, a1, n = 28) =>
  Array.from({ length: n + 1 }, (_, i) => {
    const a = a0 + ((a1 - a0) * i) / n
    return [cx + Math.cos(a) * r, cy + Math.sin(a) * r]
  })

/** The cloud's outline: three round puffs over a flat base. */
export function cloud(K) {
  const [ox, oy] = K.origin
  const pts = [[ox + K.start[0], oy + K.start[1]]]
  for (const [dx, dy, r, a0, a1] of K.puffs) pts.push(...arc(ox + dx, oy + dy, r, Math.PI * a0, Math.PI * a1))
  return pts
}

/** A spiral groove: a strip that winds inwards and thins. */
export function spiral(K, [dx, dy, r0, turns], n = 140) {
  const [ox, oy] = K.origin, w = K.spiralWidth
  const at = (t, k) => {
    const a = Math.PI / 2 + t * turns * 2 * Math.PI, r = r0 * (1 - t * 0.85) + k
    return [ox + dx + Math.cos(a) * r, oy + dy + Math.sin(a) * r]
  }
  const out = [], back = []
  for (let i = 0; i <= n; i++) out.push(at(i / n, w))
  for (let i = n; i >= 0; i--) back.push(at(i / n, -w * (1 - (i / n) * 0.5)))
  return [...out, ...back]
}

/** The keyhole: a round head over a tapered slot. `grow` scales it (the glow behind is a little larger). */
export function keyhole(K, grow = 1, n = 40) {
  const { x, y, r: r0, slot, depth } = K.keyhole
  const [ox, oy] = K.origin, cx = ox + x, cy = oy + y, r = r0 * grow
  const a = Math.asin(0.45)
  const head = Array.from({ length: n + 1 }, (_, i) => {
    const t = -Math.PI / 2 + a + ((2 * Math.PI - 2 * a) * i) / n
    return [cx + Math.cos(t) * r, cy + Math.sin(t) * r]
  })
  return [...head, [cx - r * slot, cy - r * depth], [cx + r * slot, cy - r * depth]]
}

/** The flight: tapering ribbons trailing from the cloud's base, each a little shorter and lower. */
export function tails(K, n = 30) {
  const T = K.tails, [ox, oy] = K.origin
  return Array.from({ length: T.count }, (_, i) => {
    const y0 = oy + T.y - i * T.step, len = T.length - i * T.shrink, th = T.thickness - i * T.thin, drop = T.drop + i * T.dropStep
    const x0 = ox + T.x
    const top = [], bot = []
    for (let j = 0; j <= n; j++) { const t = j / n; top.push([x0 - len * t, y0 + th * (1 - t) - drop * t * t]) }
    for (let j = n; j >= 0; j--) { const t = j / n; bot.push([x0 - len * t, y0 - th * (1 - t) - drop * t * t]) }
    return [...top, ...bot]
  })
}

/** Everything the 3D render needs, as plain arrays. */
export function crestShapes(K) {
  return {
    body: [cloud(K), ...K.spirals.map((s) => spiral(K, s)), keyhole(K)],
    tails: tails(K),
    glow: keyhole(K, K.keyhole.glow),
  }
}

/** Bounding box of a set of polygons. */
export function bounds(polys) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity
  for (const p of polys) for (const [x, y] of p) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y) }
  return { x0, y0, x1, y1 }
}
