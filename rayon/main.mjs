import { createState, step } from './logic.mjs'
import { keysToInput, padToInput } from './input.mjs'
import { cameraX, drawWorld, drawSousou } from './draw.mjs'


const canvas = document.querySelector('#jeu')
const ctx = canvas.getContext('2d')
const state = createState()
const down = new Set()
let prevKeys = new Set()
let prevButtons = { down: false, left: false, right: false }

const HELD = new Set([
  'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Space', 'KeyJ', 'KeyL',
])

addEventListener('keydown', (event) => {
  if (HELD.has(event.code)) event.preventDefault()
  down.add(event.code)
})

addEventListener('keyup', (event) => {
  down.delete(event.code)
})

addEventListener('blur', () => {
  down.clear()
})

function connectedPad() {
  const pads = navigator.getGamepads?.()
  if (!pads) return null
  for (let i = 0; i < pads.length; i++) {
    const pad = pads[i]
    if (pad && pad.connected) return pad
  }
  return null
}

function frame() {
  const pad = connectedPad()
  const input = pad ? padToInput(pad, prevButtons) : keysToInput(down, prevKeys)
  step(state, input)
  prevKeys = new Set(down)
  if (pad) {
    prevButtons = {
      down: !!pad.buttons[0]?.pressed,
      left: !!pad.buttons[2]?.pressed,
      right: !!pad.buttons[1]?.pressed,
    }
  }
  const cam = cameraX(state)
  drawWorld(ctx, cam, state)
  ctx.save()
  ctx.translate(-cam, 0)
  drawSousou(ctx, state)
  ctx.restore()
  requestAnimationFrame(frame)
}

requestAnimationFrame(frame)
