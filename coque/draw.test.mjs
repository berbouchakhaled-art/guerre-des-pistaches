import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { PALETTE, drawSousou, cameraX } from './draw.mjs'
import { createState } from './logic.mjs'

test('les couleurs verrouillées', () => {
  assert.equal(PALETTE.shirt, '#f4f4f4')
  assert.equal(PALETTE.jeans, '#3a6fbe')
  assert.equal(PALETTE.shoe, '#e23c3c')
  assert.equal(PALETTE.ink, '#1a120c')
})

test('Sousou est peint en aplats avec un contour', () => {
  const fills = []
  const strokes = []
  const ctx = {
    fillStyle: '', strokeStyle: '', lineWidth: 1,
    beginPath() {}, ellipse() {}, rect() {}, arc() {},
    moveTo() {}, lineTo() {}, save() {}, restore() {},
    translate() {},
    fill() { fills.push(this.fillStyle) },
    stroke() { strokes.push([this.strokeStyle, this.lineWidth]) },
    fillRect() { this.fill() },
    strokeRect() { this.stroke() },
  }
  drawSousou(ctx, createState())
  assert.ok(fills.includes(PALETTE.shirt))
  assert.ok(fills.includes(PALETTE.jeans))
  assert.ok(fills.includes(PALETTE.shoe))
  assert.ok(fills.includes(PALETTE.hair))
  assert.ok(strokes.some(([color, width]) => color === PALETTE.ink && width >= 4))
})

test('la caméra suit Sousou sans sortir de la salle', () => {
  assert.equal(cameraX(createState()), 0)
  const mid = createState()
  mid.x = 1000
  assert.equal(cameraX(mid), 320)
  const end = createState()
  end.x = 1590
  assert.equal(cameraX(end), 320)
})

test('la page ne découpe pas les JPEG', () => {
  const html = readFileSync(new URL('../coque.html', import.meta.url), 'utf8')
  const main = readFileSync(new URL('./main.mjs', import.meta.url), 'utf8')
  assert.equal(html.includes('art/coque'), false)
  assert.equal(main.includes('art/coque'), false)
})
