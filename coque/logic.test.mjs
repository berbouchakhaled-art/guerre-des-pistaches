import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createState, WORLD, PLATFORMS, DRIPS, step } from './logic.mjs'

test('état de départ debout sur le sol', () => {
  const s = createState()
  assert.equal(s.x, 300)
  assert.equal(s.y, WORLD.ground)
  assert.equal(s.onGround, true)
  assert.equal(s.face, 1)
  assert.equal(s.hanging, false)
  assert.equal(s.whip, 0)
  assert.deepEqual(s.nuts, [])
  assert.equal(PLATFORMS.length, 4)
  assert.equal(PLATFORMS[0].w, WORLD.width)
  assert.equal(DRIPS.length, 3)
  const next = step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(next.y, WORLD.ground)
})

test('courir à droite avance de 4 et regarde à droite', () => {
  const s = createState()
  step(s, { left: false, right: true, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.x, 304)
  assert.equal(s.face, 1)
  assert.equal(s.y, WORLD.ground)
})

test('courir à gauche avance de 4 et regarde à gauche', () => {
  const s = createState()
  step(s, { left: true, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.x, 296)
  assert.equal(s.face, -1)
})

test('gauche et droite ensemble ne bougent pas', () => {
  const s = createState()
  step(s, { left: true, right: true, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.x, 300)
})

test('espace donne une vitesse vers le haut', () => {
  const s = createState()
  step(s, { left: false, right: false, jump: true, jumpPressed: true, shoot: false, whip: false })
  assert.equal(s.vy, -12)
  assert.equal(s.y, 608)
  assert.equal(s.onGround, false)
})

test('la gravité ramène au sol', () => {
  const s = createState()
  s.y = 610
  s.onGround = false
  s.vy = 0
  step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.vy, 1)
  assert.equal(s.y, 611)
  for (let i = 0; i < 30; i++) {
    step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  }
  assert.equal(s.y, WORLD.ground)
  assert.equal(s.vy, 0)
  assert.equal(s.onGround, true)
})

test('on ne saute pas en l’air', () => {
  const s = createState()
  s.onGround = false
  s.y = 400
  s.vy = 2
  step(s, { left: false, right: false, jump: true, jumpPressed: true, shoot: false, whip: false })
  assert.notEqual(s.vy, -12)
})

test('on se pose sur la plateforme de gauche', () => {
  const s = createState()
  s.x = 200
  s.y = 486
  s.vy = 4
  s.onGround = false
  step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.y, 490)
  assert.equal(s.onGround, true)
  assert.equal(s.vy, 0)
})

test('à côté de la plateforme on tombe jusqu’au sol', () => {
  const s = createState()
  s.x = 40
  s.y = 500
  s.vy = 0
  s.onGround = false
  for (let i = 0; i < 40; i++) {
    step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  }
  assert.equal(s.y, WORLD.ground)
})

test('en l’air, espace tenu près d’un fil accroche', () => {
  const s = createState()
  s.x = 420
  s.y = 200
  s.onGround = false
  s.vy = 1
  s.face = 1
  step(s, { left: false, right: false, jump: true, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.hanging, true)
  assert.equal(s.hangId, 0)
  assert.equal(s.x, 420)
})

test('la croix balance puis relâcher lâche le fil', () => {
  const s = createState()
  s.x = 420
  s.y = 200
  s.onGround = false
  s.face = 1
  const hold = { left: false, right: true, jump: true, jumpPressed: false, shoot: false, whip: false }
  step(s, hold)
  step(s, hold)
  assert.ok(s.angle > 0)
  assert.ok(s.x > 420)
  step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.hanging, false)
  assert.ok(s.vx > 0)
  assert.equal(s.vy, -3)
})
