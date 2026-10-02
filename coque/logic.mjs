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

const JUMP = -12
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
  if (state.y >= WORLD.ground) land(state, WORLD.ground)
}

export function step(state, input) {
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
  bodies(state, input)
  return state
}
