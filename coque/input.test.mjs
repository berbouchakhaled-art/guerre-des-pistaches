import { test } from 'node:test'
import assert from 'node:assert/strict'
import { keysToInput, padToInput } from './input.mjs'

test('flèches espace J et L', () => {
  const down = new Set(['ArrowRight', 'Space', 'KeyJ', 'KeyL'])
  const prev = new Set()
  const input = keysToInput(down, prev)
  assert.equal(input.right, true)
  assert.equal(input.jump, true)
  assert.equal(input.jumpPressed, true)
  assert.equal(input.shoot, true)
  assert.equal(input.whip, true)
  const held = keysToInput(down, down)
  assert.equal(held.jumpPressed, false)
  assert.equal(held.shoot, false)
  assert.equal(held.whip, false)
  assert.equal(held.jump, true)
})

test('bouton du bas, gauche et droite de la manette', () => {
  const pad = {
    axes: [0],
    buttons: [{ pressed: true }, { pressed: true }, { pressed: true }, { pressed: false }],
  }
  const prev = { down: false, left: false, right: false }
  const input = padToInput(pad, prev)
  assert.equal(input.jump, true)
  assert.equal(input.jumpPressed, true)
  assert.equal(input.shoot, true)
  assert.equal(input.whip, true)
})
