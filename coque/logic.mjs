export const WORLD = { width: 1600, height: 720, ground: 620 }

export const PLATFORMS = [
  { x: 0, y: 620, w: 1600, h: 48 },
  { x: 160, y: 490, w: 240, h: 26 },
  { x: 640, y: 400, w: 280, h: 26 },
  { x: 1100, y: 470, w: 240, h: 26 },
]

export const DRIPS = [
  { id: 0, x: 420, y: 70, len: 240 },
  { id: 1, x: 780, y: 60, len: 200 },
  { id: 2, x: 1200, y: 80, len: 260 },
]

export function createState() {
  return {
    x: 300, y: WORLD.ground, vx: 0, vy: 0, face: 1,
    onGround: true, hanging: false, hangId: null, angle: 0,
    whip: 0, nuts: [],
  }
}

const JUMP = -22
const GRAVITY = 1
const MAX_FALL = 14

function land(state, sole) {
  state.y = sole
  state.vy = 0
  state.onGround = true
  state.hanging = false
  state.hangId = null
}

function bodies(state, input) {
  if (state.hanging) return
  if (state.onGround && input.jumpPressed) {
    state.vy = JUMP
    state.onGround = false
  } else {
    state.vy = Math.min(MAX_FALL, state.vy + GRAVITY)
  }
  state.y += state.vy
  if (state.vy >= 0) {
    for (const plat of PLATFORMS) {
      const wasAbove = state.y - state.vy <= plat.y
      const overlaps = state.x >= plat.x && state.x <= plat.x + plat.w
      if (wasAbove && state.y >= plat.y && overlaps) {
        land(state, plat.y)
        break
      }
    }
  }
  if (state.y >= WORLD.ground) land(state, WORLD.ground)
}

function hand(state) {
  return { x: state.x + state.face * 16, y: state.y - 48 }
}

function nearDrip(state) {
  const h = hand(state)
  for (const drip of DRIPS) {
    const top = drip.y
    const bot = drip.y + drip.len
    const cy = Math.max(top, Math.min(bot, h.y))
    const dx = h.x - drip.x
    const dy = h.y - cy
    if (dx * dx + dy * dy <= 36 * 36) return drip
  }
  return null
}

function hang(state, input) {
  if (state.hanging && !input.jump) {
    state.hanging = false
    state.vx = Math.sin(state.angle) * 6
    state.vy = -3
    state.hangId = null
    return
  }
  if (!state.hanging && !state.onGround && input.jump) {
    const drip = nearDrip(state)
    if (drip) {
      state.hanging = true
      state.hangId = drip.id
      state.angle = 0
      state.vy = 0
      state.onGround = false
    }
  }
  if (!state.hanging) return
  if (input.right) state.angle = Math.min(1, state.angle + 0.05)
  if (input.left) state.angle = Math.max(-1, state.angle - 0.05)
  const drip = DRIPS.find((d) => d.id === state.hangId)
  state.x = drip.x + Math.sin(state.angle) * 80
  state.y = drip.y + 48 + Math.cos(state.angle) * 80
}

export function whipBox(state) {
  if (state.whip <= 0) return null
  const w = 52
  const x = state.face === 1 ? state.x + 10 : state.x - 10 - w
  return { x, y: state.y - 36, w, h: 24 }
}

export function step(state, input) {
  if (input.whip && state.whip === 0) state.whip = 8
  else if (state.whip > 0) state.whip -= 1
  const wasHanging = state.hanging
  hang(state, input)
  if (!wasHanging && !state.hanging) {
    const SPEED = 4
    if (input.left && !input.right) {
      state.face = -1
      state.vx = -SPEED
    } else if (input.right && !input.left) {
      state.face = 1
      state.vx = SPEED
    } else {
      state.vx = 0
    }
    if (!state.hanging) state.x += state.vx
    state.x = Math.max(20, Math.min(WORLD.width - 20, state.x))
    bodies(state, input)
  }
  if (input.shoot && state.nuts.length === 0) {
    state.nuts.push({ x: state.x + state.face * 28, y: state.y - 40, vx: 8 * state.face })
  }
  for (const nut of state.nuts) nut.x += nut.vx
  state.nuts = state.nuts.filter((nut) => nut.x > 0 && nut.x < WORLD.width)
  return state
}
