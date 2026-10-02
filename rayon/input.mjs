export function keysToInput(down, prev) {
  const jump = down.has('Space')
  return {
    left: down.has('ArrowLeft'),
    right: down.has('ArrowRight'),
    jump,
    jumpPressed: jump && !prev.has('Space'),
    shoot: down.has('KeyJ') && !prev.has('KeyJ'),
    whip: down.has('KeyL') && !prev.has('KeyL'),
  }
}

export function padToInput(pad, prevButtons) {
  const axis = pad.axes[0] || 0
  const jump = pad.buttons[0].pressed
  const whip = pad.buttons[1].pressed
  const shoot = pad.buttons[2].pressed
  const left = axis < -0.5 || (pad.buttons[14] && pad.buttons[14].pressed)
  const right = axis > 0.5 || (pad.buttons[15] && pad.buttons[15].pressed)
  return {
    left, right, jump,
    jumpPressed: jump && !prevButtons.down,
    shoot: shoot && !prevButtons.left,
    whip: whip && !prevButtons.right,
  }
}
