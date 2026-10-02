import { WORLD, PLATFORMS, DRIPS, whipBox } from './logic.mjs'

export const PALETTE = {
  shirt: '#f4f4f4',
  jeans: '#3a6fbe',
  shoe: '#e23c3c',
  hair: '#6b4423',
  skin: '#f0c09a',
  ink: '#1a120c',
  shell: '#3f9d34',
  cream: '#f3e6c0',
  caramel: '#d4a017',
}

const SOLE = '#f7f7f7'
const KERNEL = '#b6d36e'
const CORD = '#5c3a1e'
const SHELL_TIP = '#c6d45a'
const KERNEL_TIP = '#7cb342'
const CRACK = '#d8ff9a'

const CEILING = [
  [150, 96, 70],
  [250, 88, 100],
  [560, 84, 90],
  [660, 96, 64],
  [980, 80, 100],
  [1080, 92, 72],
  [1400, 86, 96],
  [1510, 98, 60],
]

export function cameraX(state) {
  return Math.max(0, Math.min(WORLD.width - 1280, state.x - 640))
}

function ink(ctx, width = 4) {
  ctx.strokeStyle = PALETTE.ink
  ctx.lineWidth = width
}

function strokeCrack(ctx, points, width) {
  ctx.beginPath()
  ctx.moveTo(points[0][0], points[0][1])
  for (let i = 1; i < points.length; i++) ctx.lineTo(points[i][0], points[i][1])
  ctx.strokeStyle = CRACK
  ctx.lineWidth = width
  ctx.stroke()
}

function drawDrip(ctx, x, y, len) {
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x, y + len)
  ctx.strokeStyle = PALETTE.caramel
  ctx.lineWidth = 6
  ctx.stroke()
  ctx.fillStyle = PALETTE.caramel
  ctx.beginPath()
  ctx.ellipse(x, y + len, 7, 11, 0, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx, 3)
  ctx.stroke()
  ctx.fillStyle = '#f0c84a'
  ctx.beginPath()
  ctx.ellipse(x - 2, y + len - 2, 2, 4, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawStrand(ctx, x, y, len) {
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x, y + len)
  ctx.strokeStyle = '#e7c98a'
  ctx.lineWidth = 2
  ctx.stroke()
  ctx.fillStyle = '#f3ddb0'
  ctx.beginPath()
  ctx.ellipse(x, y + len, 2.5, 4, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawKernel(ctx, plat) {
  ctx.fillStyle = KERNEL
  ctx.fillRect(plat.x, plat.y, plat.w, plat.h)
  ctx.fillStyle = PALETTE.cream
  ctx.fillRect(plat.x, plat.y, plat.w, Math.max(6, plat.h * 0.42))
  ctx.fillStyle = '#e7f6bf'
  const spots = Math.max(2, Math.floor(plat.w / 56))
  for (let i = 0; i < spots; i++) {
    ctx.beginPath()
    ctx.ellipse(plat.x + 24 + i * 52, plat.y + plat.h * 0.7, 5, 3, 0, 0, Math.PI * 2)
    ctx.fill()
  }
  ink(ctx)
  ctx.strokeRect(plat.x, plat.y, plat.w, plat.h)
}

function drawLight(ctx, x) {
  ctx.strokeStyle = '#2a241c'
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(x, 0)
  ctx.lineTo(x, 28)
  ctx.moveTo(x + 220, 0)
  ctx.lineTo(x + 220, 28)
  ctx.stroke()
  ctx.fillStyle = '#3a342c'
  ctx.fillRect(x, 28, 220, 16)
  ink(ctx, 3)
  ctx.strokeRect(x, 28, 220, 16)
  ctx.fillStyle = '#e7f6c8'
  ctx.fillRect(x + 8, 34, 204, 6)
}

function drawBox(ctx, x, y, w, h, fill) {
  ctx.fillStyle = fill
  ctx.fillRect(x, y - h, w, h)
  ink(ctx, 3)
  ctx.strokeRect(x, y - h, w, h)
  ctx.fillStyle = '#f4f1e4'
  ctx.beginPath()
  ctx.ellipse(x + w * 0.35, y - h * 0.45, 7, 5, 0, 0, Math.PI * 2)
  ctx.ellipse(x + w * 0.62, y - h * 0.5, 6, 4, 0.4, 0, Math.PI * 2)
  ctx.fill()
}

function drawTag(ctx, tag) {
  const top = tag.y + 8
  const bot = tag.y + tag.len
  ctx.strokeStyle = '#1a120c'
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(tag.x, tag.y)
  ctx.lineTo(tag.x, top + 6)
  ctx.stroke()
  ctx.fillStyle = '#f2d34a'
  ctx.fillRect(tag.x - 14, top, 28, bot - top)
  ink(ctx, 3)
  ctx.strokeRect(tag.x - 14, top, 28, bot - top)
  ctx.beginPath()
  ctx.arc(tag.x, top + 8, 3, 0, Math.PI * 2)
  ctx.stroke()
}

function drawStall(ctx, plat) {
  const front = 108
  ctx.fillStyle = '#c4a574'
  ctx.fillRect(plat.x, plat.y, plat.w, 16)
  ctx.fillStyle = '#a67c52'
  ctx.fillRect(plat.x, plat.y + 16, plat.w, front - 16)
  ink(ctx, 4)
  ctx.strokeRect(plat.x, plat.y, plat.w, front)
  ctx.beginPath()
  ctx.moveTo(plat.x, plat.y + 16)
  ctx.lineTo(plat.x + plat.w, plat.y + 16)
  ctx.stroke()
}

export function drawWorld(ctx, cam) {
  ctx.save()
  ctx.translate(-cam, 0)

  ctx.fillStyle = '#e7e4d4'
  ctx.fillRect(0, 0, WORLD.width, WORLD.ground)
  drawLight(ctx, 180)
  drawLight(ctx, 980)

  const floor = PLATFORMS[0]
  ctx.fillStyle = '#e6c98a'
  ctx.fillRect(floor.x, floor.y, floor.w, 160)
  ctx.strokeStyle = '#f3e2b4'
  ctx.lineWidth = 2
  for (let y = floor.y + 18; y < 720; y += 16) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(WORLD.width, y)
    ctx.stroke()
  }
  ink(ctx, 5)
  ctx.beginPath()
  ctx.moveTo(0, floor.y)
  ctx.lineTo(WORLD.width, floor.y)
  ctx.stroke()

  const stalls = PLATFORMS.slice(1)
  for (const plat of stalls) drawStall(ctx, plat)
  drawBox(ctx, 110, 430, 70, 36, '#8fce6a')
  drawBox(ctx, 190, 430, 70, 36, '#8fce6a')
  drawBox(ctx, 196, 394, 58, 36, '#8fce6a')
  drawBox(ctx, 600, 360, 72, 40, '#8fce6a')
  drawBox(ctx, 680, 360, 72, 40, '#b48ad4')
  drawBox(ctx, 760, 320, 66, 40, '#b48ad4')
  drawBox(ctx, 1080, 420, 70, 36, '#8fce6a')
  drawBox(ctx, 1160, 420, 70, 36, '#b48ad4')
  for (const tag of DRIPS) drawTag(ctx, tag)

  ctx.restore()
}

function drawShoe(ctx, sx, sy) {
  ctx.fillStyle = PALETTE.shoe
  ctx.fillRect(sx, sy, 14, 8)
  ink(ctx)
  ctx.strokeRect(sx, sy, 14, 8)
  ctx.fillStyle = SOLE
  ctx.fillRect(sx + 2, sy + 5, 10, 4)
  ctx.beginPath()
  ctx.moveTo(sx + 1, sy + 9)
  ctx.lineTo(sx + 13, sy + 9)
  ctx.stroke()
}

function drawShirt(ctx, x, y) {
  ctx.fillStyle = PALETTE.shirt
  ctx.fillRect(x - 18, y - 68, 36, 40)
  ink(ctx)
  ctx.strokeRect(x - 18, y - 68, 36, 40)
  ctx.fillStyle = PALETTE.shirt
  ctx.fillRect(x - 24, y - 66, 12, 10)
  ctx.fillRect(x + 12, y - 66, 12, 10)
  ctx.strokeRect(x - 24, y - 66, 12, 10)
  ctx.strokeRect(x + 12, y - 66, 12, 10)
  ctx.fillStyle = PALETTE.skin
  ctx.beginPath()
  ctx.arc(x, y - 66, 5, 0, Math.PI)
  ctx.fill()
}

function drawForearm(ctx, ax, ay, w, h) {
  ctx.fillStyle = PALETTE.skin
  ctx.fillRect(ax, ay, w, h)
  ink(ctx)
  ctx.strokeRect(ax, ay, w, h)
  ctx.beginPath()
  ctx.arc(ax + w / 2, ay + h, 4.5, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

function drawSideArms(ctx, x, y) {
  drawForearm(ctx, x - 26, y - 56, 9, 16)
  drawForearm(ctx, x + 17, y - 56, 9, 16)
}

function drawAimArm(ctx, x, y, f) {
  const ax = f > 0 ? 14 : -28
  ctx.fillStyle = PALETTE.skin
  ctx.fillRect(x + ax, y - 46, 14, 7)
  ink(ctx)
  ctx.strokeRect(x + ax, y - 46, 14, 7)
  ctx.beginPath()
  ctx.arc(x + f * 28, y - 42, 4, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

function drawWhipArm(ctx, x, y, f) {
  const ax = f > 0 ? 8 : -30
  ctx.fillStyle = PALETTE.skin
  ctx.fillRect(x + ax, y - 58, 22, 8)
  ink(ctx)
  ctx.strokeRect(x + ax, y - 58, 22, 8)
  ctx.beginPath()
  ctx.arc(x + f * 28, y - 54, 5, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

function drawFace(ctx, x, y, f) {
  const hy = y - 84
  const ox = f * 3
  ctx.fillStyle = '#fffef8'
  ctx.beginPath()
  ctx.ellipse(x + ox - 5, hy - 2, 3.2, 4, 0, 0, Math.PI * 2)
  ctx.ellipse(x + ox + 5, hy - 2, 3.2, 4, 0, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx, 2)
  ctx.stroke()
  ctx.fillStyle = '#3a2416'
  ctx.beginPath()
  ctx.ellipse(x + ox - 4 + f, hy - 1, 1.7, 2.2, 0, 0, Math.PI * 2)
  ctx.ellipse(x + ox + 6 + f, hy - 1, 1.7, 2.2, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#ffffff'
  ctx.beginPath()
  ctx.ellipse(x + ox - 4.8, hy - 2.2, 0.7, 0.7, 0, 0, Math.PI * 2)
  ctx.ellipse(x + ox + 5.2, hy - 2.2, 0.7, 0.7, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.strokeStyle = PALETTE.hair
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x + ox - 8, hy - 9)
  ctx.lineTo(x + ox - 2, hy - 8)
  ctx.moveTo(x + ox + 2, hy - 8)
  ctx.lineTo(x + ox + 8, hy - 9)
  ctx.stroke()
  ctx.strokeStyle = '#d9a27e'
  ctx.beginPath()
  ctx.moveTo(x + ox + f, hy + 2)
  ctx.lineTo(x + ox + f * 2, hy + 6)
  ctx.stroke()
  ink(ctx, 2)
  ctx.beginPath()
  ctx.arc(x + ox + f, hy + 8, 3, 0.15, Math.PI - 0.15)
  ctx.stroke()
  ctx.fillStyle = '#e8a090'
  ctx.beginPath()
  ctx.ellipse(x + ox - 11, hy + 4, 2.5, 1.6, 0, 0, Math.PI * 2)
  ctx.ellipse(x + ox + 11, hy + 4, 2.5, 1.6, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawHairMass(ctx, x, hy, f) {
  const b = -f
  const locks = [
    [b * 8, -8, 14, 11],
    [b * 16, 4, 8, 11],
    [b * 14, 18, 7, 9],
    [b * 8, 30, 6, 7],
    [f * 15, 2, 6, 9],
    [f * 13, 16, 5, 7],
  ]
  ctx.fillStyle = PALETTE.hair
  ink(ctx)
  for (const [dx, dy, rx, ry] of locks) {
    ctx.beginPath()
    ctx.ellipse(x + dx, hy + dy, rx, ry, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.stroke()
  }
  ctx.beginPath()
  ctx.arc(x - 9, hy - 16, 8, Math.PI, Math.PI * 2)
  ctx.arc(x + 2, hy - 20, 8, Math.PI, Math.PI * 2)
  ctx.arc(x + 12, hy - 15, 7, Math.PI, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
}

function drawHead(ctx, x, y, f) {
  const hy = y - 84
  drawHairMass(ctx, x, hy, f)
  ctx.fillStyle = PALETTE.skin
  ctx.fillRect(x - 5, y - 76, 10, 12)
  ctx.beginPath()
  ctx.ellipse(x - 16, hy, 3.5, 5, 0, 0, Math.PI * 2)
  ctx.ellipse(x + 16, hy, 3.5, 5, 0, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx, 3)
  ctx.stroke()
  ctx.fillStyle = PALETTE.skin
  ctx.beginPath()
  ctx.arc(x, hy, 16, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx)
  ctx.stroke()
  drawFace(ctx, x, y, f)
  ctx.fillStyle = PALETTE.hair
  ink(ctx)
  ctx.beginPath()
  ctx.arc(x, hy - 5, 16, Math.PI, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  ctx.beginPath()
  ctx.arc(x - 8, hy - 12, 6, Math.PI, Math.PI * 2)
  ctx.arc(x + 2, hy - 15, 6, Math.PI, Math.PI * 2)
  ctx.arc(x + 11, hy - 11, 5, Math.PI, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  ctx.strokeStyle = '#8d5a32'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.arc(x - f * 12, hy + 10, 8, Math.PI * 0.15, Math.PI * 1.15)
  ctx.stroke()
  ctx.beginPath()
  ctx.arc(x + f * 4, hy - 14, 7, Math.PI * 1.1, Math.PI * 1.8)
  ctx.stroke()
}

function drawStand(ctx, x, y, f, whipping) {
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - 14, y - 40, 28, 34)
  ctx.fillStyle = '#2c5c9e'
  ctx.fillRect(x - 14, y - 12, 28, 6)
  ink(ctx)
  ctx.strokeRect(x - 14, y - 40, 28, 34)
  ctx.beginPath()
  ctx.moveTo(x, y - 28)
  ctx.lineTo(x, y - 8)
  ctx.stroke()
  drawShirt(ctx, x, y)
  if (whipping) drawWhipArm(ctx, x, y, f)
  else drawSideArms(ctx, x, y)
  drawShoe(ctx, x - 16, y - 8)
  drawShoe(ctx, x + 2, y - 8)
  drawHead(ctx, x, y, f)
}

function drawRun(ctx, x, y, f, whipping) {
  const stride = Math.sin(x * 0.12)
  const bob = Math.abs(stride) * 3
  const py = y - bob
  const front = f * (8 + stride * 8)
  const back = -f * (10 + stride * 6)
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - 14, py - 40, 28, 16)
  ink(ctx)
  ctx.strokeRect(x - 14, py - 40, 28, 16)
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x + front - 6, py - 32, 12, 26)
  ctx.fillRect(x + back - 6, py - 30, 12, 16)
  ink(ctx)
  ctx.strokeRect(x + front - 6, py - 32, 12, 26)
  ctx.strokeRect(x + back - 6, py - 30, 12, 16)
  drawShoe(ctx, x + front - 8, py - 8)
  drawShoe(ctx, x + back - 8, py - 18)
  drawShirt(ctx, x + f * 2, py)
  if (whipping) drawWhipArm(ctx, x, py, f)
  else {
    drawForearm(ctx, x - f * (18 + stride * 4), py - 58, 8, 16)
    drawForearm(ctx, x + f * 16, py - 64, 12, 10)
  }
  drawHead(ctx, x + f * 2, py, f)
}

function drawJump(ctx, x, y, f, whipping) {
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - 14, y - 40, 28, 14)
  ink(ctx)
  ctx.strokeRect(x - 14, y - 40, 28, 14)
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - 16, y - 32, 12, 16)
  ctx.fillRect(x + f * 6, y - 36, 16, 10)
  ink(ctx)
  ctx.strokeRect(x - 16, y - 32, 12, 16)
  ctx.strokeRect(x + f * 6, y - 36, 16, 10)
  drawShoe(ctx, x - 18, y - 18)
  drawShoe(ctx, x + f * 12, y - 30)
  drawShirt(ctx, x, y)
  if (whipping) drawWhipArm(ctx, x, y, f)
  else {
    drawForearm(ctx, x - 28, y - 78, 8, 14)
    drawForearm(ctx, x + 20, y - 78, 8, 14)
  }
  drawHead(ctx, x, y, f)
}

function drawClosedHand(ctx, x, y, side, drip) {
  const gy = Math.max(drip.y + 8, Math.min(drip.y + drip.len - 12, y - 104))
  const gx = drip.x
  ctx.beginPath()
  ctx.moveTo(x + side * 18, y - 60)
  ctx.lineTo(x + side * 28, y - 86)
  ctx.lineTo(gx, gy)
  ink(ctx, 9)
  ctx.stroke()
  ctx.strokeStyle = PALETTE.skin
  ctx.lineWidth = 5
  ctx.stroke()
  ctx.fillStyle = PALETTE.skin
  ctx.beginPath()
  ctx.arc(gx, gy, 7, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx, 3)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(gx, gy - 8)
  ctx.lineTo(gx, gy + 8)
  ctx.strokeStyle = '#f2d34a'
  ctx.lineWidth = 4
  ctx.stroke()
  ink(ctx, 2)
  ctx.beginPath()
  ctx.arc(gx, gy, 4, 0.15, Math.PI - 0.15)
  ctx.stroke()
}

function drawHang(ctx, state, x, y, f) {
  const drip = DRIPS.find((d) => d.id === state.hangId)
  const side = drip ? Math.sign(drip.x - x) || f : f
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - 14, y - 40, 28, 22)
  ink(ctx)
  ctx.strokeRect(x - 14, y - 40, 28, 22)
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - f * 10, y - 24, 12, 16)
  ctx.fillRect(x + f * 4, y - 26, 14, 12)
  ink(ctx)
  ctx.strokeRect(x - f * 10, y - 24, 12, 16)
  ctx.strokeRect(x + f * 4, y - 26, 14, 12)
  drawShoe(ctx, x - f * 12, y - 12)
  drawShoe(ctx, x + f * 6, y - 18)
  drawShirt(ctx, x, y)
  drawForearm(ctx, x - side * 24, y - 56, 8, 14)
  drawHead(ctx, x, y, f)
  if (drip) drawClosedHand(ctx, x, y, side, drip)
}

function whipArc(ctx, x0, y0, x1, y1, bow) {
  const dx = x1 - x0
  const dy = y1 - y0
  const d = Math.hypot(dx, dy) || 1
  let ux = -dy / d
  let uy = dx / d
  if (uy > 0) {
    ux = -ux
    uy = -uy
  }
  const s = Math.min(Math.max(bow, 6), d * 0.45)
  const radius = (d * d) / (8 * s) + s / 2
  const cx = (x0 + x1) / 2 - ux * (radius - s)
  const cy = (y0 + y1) / 2 - uy * (radius - s)
  const a0 = Math.atan2(y0 - cy, x0 - cx)
  const a1 = Math.atan2(y1 - cy, x1 - cx)
  let sweep = a1 - a0
  while (sweep > Math.PI) sweep -= Math.PI * 2
  while (sweep < -Math.PI) sweep += Math.PI * 2
  ctx.arc(cx, cy, radius, a0, a1, sweep < 0)
}

function drawWhip(ctx, state) {
  const box = whipBox(state)
  if (!box) return
  const f = state.face === -1 ? -1 : 1
  const t = Math.min(1, Math.max(0, (8 - state.whip) / 7))
  const reach = Math.sin(t * Math.PI)
  const handX = state.x + f * 28
  const handY = state.y - 54
  const farX = f > 0 ? box.x + box.w : box.x
  const tipX = handX + (farX - handX) * (0.28 + 0.72 * reach)
  const tipY = state.y - 36 - 14 * reach
  ctx.beginPath()
  whipArc(ctx, handX, handY, tipX, tipY, 8 + reach * 18)
  ink(ctx, 5)
  ctx.stroke()
  ctx.strokeStyle = CORD
  ctx.lineWidth = 2
  ctx.stroke()
  ctx.fillStyle = SHELL_TIP
  ctx.beginPath()
  ctx.ellipse(tipX, tipY, 12, 8, f * -0.4, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx, 3)
  ctx.stroke()
  ctx.fillStyle = KERNEL_TIP
  ctx.beginPath()
  ctx.ellipse(tipX, tipY, 5.5, 3.2, f * -0.4, 0, Math.PI * 2)
  ctx.fill()
}

function drawNut(ctx, x, y) {
  ctx.fillStyle = SHELL_TIP
  ctx.beginPath()
  ctx.ellipse(x, y, 8, 5, 0, 0, Math.PI * 2)
  ctx.fill()
  ink(ctx, 2)
  ctx.stroke()
  ctx.fillStyle = KERNEL_TIP
  ctx.beginPath()
  ctx.ellipse(x, y, 3.6, 2.2, 0, 0, Math.PI * 2)
  ctx.fill()
}

export function drawSousou(ctx, state) {
  const x = state.x
  const y = state.y
  const f = state.face === -1 ? -1 : 1
  const whipping = state.whip > 0
  if (state.hanging) drawHang(ctx, state, x, y, f)
  else if (state.vx !== 0) drawRun(ctx, x, y, f, whipping)
  else if (!state.onGround) drawJump(ctx, x, y, f, whipping)
  else drawStand(ctx, x, y, f, whipping)
  if (state.nuts.length > 0 && !state.hanging) drawAimArm(ctx, x, y, f)
  if (whipping) drawWhip(ctx, state)
  for (const nut of state.nuts) drawNut(ctx, nut.x, nut.y)
}
