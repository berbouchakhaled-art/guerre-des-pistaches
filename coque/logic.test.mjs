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
