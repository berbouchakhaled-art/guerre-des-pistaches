# Dans la coque — plan d’implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ouvrir `coque.html` et jouer Sousou dans la pistache : courir, sauter, s’accrocher au caramel, tirer une pistache, donner un coup de fouet, au clavier et à la manette.

**Architecture:** La physique est dans `coque/logic.mjs`, sans canvas, testée par `node --test`. Le dessin est dans `coque/draw.mjs` (formes, pas les JPEG). `coque/main.mjs` lit le clavier et la manette, appelle `step`, dessine. `index.html` et la ROM NES ne sont pas modifiés.

**Tech Stack:** HTML, CSS, JavaScript en modules, canvas 2D, `node --test`. Pas de framework, pas de build.

**Spec:** `docs/superpowers/specs/2026-10-02-sousou-coque-design.md`

## Global Constraints

- Page nouvelle `coque.html` à côté de `index.html`. `index.html` reste tel quel. La ROM NES du stick n’est pas touchée.
- Sousou est dessiné en formes : cheveux châtains ondulés, t-shirt blanc dont le bas passe sur le jean, jean entier, baskets rouges, contour noir épais. On ne découpe pas les JPEG de `art/coque/`.
- Une salle. Sol sur toute la largeur. Trois plateformes d’amande : basse à gauche, milieu, droite. Fils de caramel au plafond. Fissure de lumière verte.
- Pas d’ennemis, pas de score, pas de vies, pas de raisins secs, pas de deuxième arme.
- Une pistache tirée à la fois. Elle sort de l’écran et disparaît. Elle ne casse rien.
- Clavier : flèches, Espace (saut et caramel), J (tir), L (fouet).
- Manette : croix, bouton du bas (saut et caramel), bouton de gauche (tir), bouton de droite (fouet).
- En l’air, si un fil est à portée et que le saut est tenu, Sousou pend au fil. Les flèches ou la croix le balancent. Il lâche quand on relâche le saut.

---

### Task 1: Module de physique vide

**Files:**
- Create: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: rien
- Produces:
  - `WORLD = { width: 1600, height: 720, ground: 620 }`
  - `PLATFORMS` tableau de `{ x, y, w, h }` (le `y` est le haut de la plateforme)
  - `DRIPS` tableau de `{ id, x, y, len }`
  - `createState()` retourne `{ x, y, vx, vy, face, onGround, hanging, hangId, angle, whip, nuts }`
  - `step(state, input)` modifie `state` et le retourne
  - `input` est `{ left, right, jump, jumpPressed, shoot, whip }` tous booléens
  - `y` est la semelle. `x` est le centre. `face` vaut `1` (droite) ou `-1` (gauche)

- [ ] **Step 1: Write the failing test**

```js
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL, module introuvable

- [ ] **Step 3: Write minimal implementation**

```js
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

export function step(state, input) {
  if (!input.left && !input.right && !input.jump && state.onGround) {
    state.vy = 0
    state.y = WORLD.ground
  }
  return state
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git init
git add coque/logic.mjs coque/logic.test.mjs docs/superpowers/specs/2026-10-02-sousou-coque-design.md docs/superpowers/plans/2026-10-02-sousou-coque.md art/coque
git commit -m "feat: start coque physics with a standing Sousou"
```

---

### Task 2: Courir à gauche et à droite

**Files:**
- Modify: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: `createState`, `step`
- Produces: même `step`. Vitesse horizontale `4` pixels par appel. `face` suit la direction.

- [ ] **Step 1: Write the failing test**

```js
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL, `s.x` reste 300

- [ ] **Step 3: Write minimal implementation**

Dans `step`, remplacer le bloc horizontal par :

```js
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
```

Garder le rappel au sol du task 1 tant que le saut n’existe pas.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/logic.mjs coque/logic.test.mjs
git commit -m "feat: run left and right in the shell"
```

---

### Task 3: Saut, gravité, sol

**Files:**
- Modify: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: `step`, `WORLD.ground`
- Produces: `JUMP = -12`, gravité `+1` par appel, chute plafonnée à `14`. Atterrir sur `WORLD.ground` remet `vy` à 0 et `onGround` à true.

- [ ] **Step 1: Write the failing test**

```js
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL sur `s.vy`

- [ ] **Step 3: Write minimal implementation**

```js
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
```

Appeler `bodies` après le déplacement horizontal. Retirer l’ancien rappel au sol qui ignorait le saut.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/logic.mjs coque/logic.test.mjs
git commit -m "feat: jump and fall onto the shell floor"
```

---

### Task 4: Trois plateformes

**Files:**
- Modify: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: `PLATFORMS`, `step`
- Produces: atterrissage sur le haut d’une plateforme si la semelle la traverse en descendant et que `x` est au-dessus d’elle. Largeur du corps utilisée pour le test : 40 px, donc overlap si `state.x` est entre `plat.x` et `plat.x + plat.w`.

- [ ] **Step 1: Write the failing test**

```js
test('on se pose sur la plateforme de gauche', () => {
  const s = createState()
  s.x = 200
  s.y = 480
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL, `y` n’est pas 490

- [ ] **Step 3: Write minimal implementation**

Après `state.y += state.vy`, avant le sol :

```js
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
```

Le sol est `PLATFORMS[0]`. Le test du sol du task 3 doit continuer à passer.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/logic.mjs coque/logic.test.mjs
git commit -m "feat: land on the three kernel platforms"
```

---

### Task 5: S’accrocher au caramel

**Files:**
- Modify: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: `DRIPS`, `step`
- Produces: `hanging`, `hangId`, `angle`. La main est au point `(x + face * 16, y - 48)`. Portée : 36 px du segment vertical du fil. Pendant l’accroche, `x = drip.x + Math.sin(angle) * 80`, `y = drip.y + 48 + Math.cos(angle) * 80`. Chaque flèche ajoute `0.05` à `angle`, borné à `-1` et `1`. Relâcher `jump` donne `vx = Math.sin(angle) * 6` et `vy = -3`.

- [ ] **Step 1: Write the failing test**

```js
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL, `hanging` est false

- [ ] **Step 3: Write minimal implementation**

```js
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
```

Appeler `hang` au début de `step`, et ne pas appliquer gravité ni course horizontale quand `state.hanging` est true.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/logic.mjs coque/logic.test.mjs
git commit -m "feat: swing from caramel drips"
```

---

### Task 6: Tirer une pistache

**Files:**
- Modify: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: `step`
- Produces: `state.nuts` éléments `{ x, y, vx }`. `shoot: true` ajoute une noix si le tableau est vide. `vx` vaut `8 * face`. Chaque `step` ajoute `vx` à `x`. Si `x` sort de `[0, WORLD.width]`, la noix est retirée.

- [ ] **Step 1: Write the failing test**

```js
test('J tire une seule pistache vers la droite', () => {
  const s = createState()
  const fire = { left: false, right: false, jump: false, jumpPressed: false, shoot: true, whip: false }
  step(s, fire)
  assert.equal(s.nuts.length, 1)
  assert.equal(s.nuts[0].vx, 8)
  assert.ok(s.nuts[0].x > s.x)
  step(s, fire)
  assert.equal(s.nuts.length, 1)
})

test('la pistache disparaît hors de la salle', () => {
  const s = createState()
  s.nuts.push({ x: WORLD.width - 4, y: 500, vx: 8 })
  step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.nuts.length, 0)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL, `nuts.length` vaut 0

- [ ] **Step 3: Write minimal implementation**

À la fin de `step` :

```js
if (input.shoot && state.nuts.length === 0) {
  state.nuts.push({ x: state.x + state.face * 28, y: state.y - 40, vx: 8 * state.face })
}
for (const nut of state.nuts) nut.x += nut.vx
state.nuts = state.nuts.filter((nut) => nut.x > 0 && nut.x < WORLD.width)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/logic.mjs coque/logic.test.mjs
git commit -m "feat: fire one pistachio at a time"
```

---

### Task 7: Fouet

**Files:**
- Modify: `coque/logic.mjs`
- Test: `coque/logic.test.mjs`

**Interfaces:**
- Consumes: `step`
- Produces: `state.whip` compte à rebours. `whip: true` le met à `8` s’il est à 0. Chaque `step` suivant le diminue de 1 jusqu’à 0. `whipBox(state)` retourne `null` si `whip === 0`, sinon `{ x, y, w, h }` devant Sousou : `x` commence à `state.x + state.face * 10` (si face négative, `x` est le bord gauche), `y = state.y - 36`, `w = 52`, `h = 24`.

- [ ] **Step 1: Write the failing test**

```js
import { whipBox } from './logic.mjs'

test('L déclenche un fouet de 8 images', () => {
  const s = createState()
  step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: true })
  assert.equal(s.whip, 8)
  const box = whipBox(s)
  assert.equal(box.w, 52)
  assert.ok(box.x > s.x)
  step(s, { left: false, right: false, jump: false, jumpPressed: false, shoot: false, whip: false })
  assert.equal(s.whip, 7)
})

test('sans fouet il n’y a pas de boîte', () => {
  assert.equal(whipBox(createState()), null)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/logic.test.mjs`
Expected: FAIL, `whipBox` introuvable

- [ ] **Step 3: Write minimal implementation**

```js
export function whipBox(state) {
  if (state.whip <= 0) return null
  const w = 52
  const x = state.face === 1 ? state.x + 10 : state.x - 10 - w
  return { x, y: state.y - 36, w, h: 24 }
}
```

Dans `step`, avant le reste :

```js
if (input.whip && state.whip === 0) state.whip = 8
else if (state.whip > 0) state.whip -= 1
```

Si `input.whip` est true et `whip` vient d’être mis à 8, ne pas décrémenter dans le même appel.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/logic.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/logic.mjs coque/logic.test.mjs
git commit -m "feat: swing the pistachio-shell whip"
```

---

### Task 8: Clavier et manette

**Files:**
- Create: `coque/input.mjs`
- Test: `coque/input.test.mjs`

**Interfaces:**
- Consumes: rien du canvas
- Produces:
  - `keysToInput(down, prev)` où `down` et `prev` sont des `Set` de `event.code`
  - `padToInput(pad, prevButtons)` où `pad` est un `Gamepad` et `prevButtons` un objet `{ down, left, right }`
  - Les deux retournent `{ left, right, jump, jumpPressed, shoot, whip }`
  - Codes clavier : `ArrowLeft`, `ArrowRight`, `Space`, `KeyJ`, `KeyL`
  - Manette : axe 0 ou boutons 14 et 15 pour la croix. Bouton 0 = bas = saut. Bouton 2 = gauche = tir. Bouton 1 = droite = fouet. Seuil d’axe : `0.5`

- [ ] **Step 1: Write the failing test**

```js
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/input.test.mjs`
Expected: FAIL, module introuvable

- [ ] **Step 3: Write minimal implementation**

```js
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/input.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add coque/input.mjs coque/input.test.mjs
git commit -m "feat: map keyboard and gamepad onto the shell moves"
```

---

### Task 9: Page, décor, Sousou

**Files:**
- Create: `coque.html`
- Create: `coque/draw.mjs`
- Create: `coque/main.mjs`
- Test: `coque/draw.test.mjs`

**Interfaces:**
- Consumes: `createState`, `step`, `WORLD`, `PLATFORMS`, `DRIPS`, `whipBox`, `keysToInput`, `padToInput`
- Produces:
  - `PALETTE` avec `shirt: '#f4f4f4'`, `jeans: '#3a6fbe'`, `shoe: '#e23c3c'`, `hair: '#6b4423'`, `skin: '#f0c09a'`, `ink: '#1a120c'`, `shell: '#3f9d34'`, `cream: '#f3e6c0'`, `caramel: '#d4a017'`
  - `cameraX(state)` retourne un nombre entre 0 et `WORLD.width - 1280`
  - `drawWorld(ctx, cameraX, state)` et `drawSousou(ctx, state)`
  - `drawSousou` n’appelle que `beginPath`, `ellipse`, `rect`, `arc`, `moveTo`, `lineTo`, `fill`, `stroke`, `save`, `restore`, `translate`
  - `coque.html` affiche un canvas 1280×720, fond coque, Sousou qui suit la caméra

- [ ] **Step 1: Write the failing test**

```js
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
  assert.equal(cameraX(mid), 360)
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test coque/draw.test.mjs`
Expected: FAIL, module ou `coque.html` introuvable

- [ ] **Step 3: Write minimal implementation**

`coque/draw.mjs` commence ainsi. Le t-shirt est dessiné après le jean et son rectangle descend jusqu’à `y - 28`, alors que le jean commence à `y - 40`, donc le bas du t-shirt couvre la ceinture.

```js
export const PALETTE = {
  shirt: '#f4f4f4', jeans: '#3a6fbe', shoe: '#e23c3c',
  hair: '#6b4423', skin: '#f0c09a', ink: '#1a120c',
  shell: '#3f9d34', cream: '#f3e6c0', caramel: '#d4a017',
}

export function cameraX(state) {
  return Math.max(0, Math.min(WORLD.width - 1280, state.x - 640))
}

export function drawSousou(ctx, state) {
  const x = state.x
  const y = state.y
  ctx.lineWidth = 4
  ctx.strokeStyle = PALETTE.ink
  ctx.fillStyle = PALETTE.jeans
  ctx.fillRect(x - 14, y - 40, 28, 34)
  ctx.strokeRect(x - 14, y - 40, 28, 34)
  ctx.fillStyle = PALETTE.shirt
  ctx.fillRect(x - 18, y - 68, 36, 40)
  ctx.strokeRect(x - 18, y - 68, 36, 40)
  ctx.fillStyle = PALETTE.skin
  ctx.beginPath()
  ctx.arc(x, y - 86, 16, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  ctx.fillStyle = PALETTE.hair
  ctx.beginPath()
  ctx.arc(x, y - 92, 18, Math.PI, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  ctx.fillStyle = PALETTE.shoe
  ctx.fillRect(x - 16, y - 8, 14, 8)
  ctx.fillRect(x + 2, y - 8, 14, 8)
  ctx.strokeRect(x - 16, y - 8, 14, 8)
  ctx.strokeRect(x + 2, y - 8, 14, 8)
}
```

`fillRect` et `strokeRect` sont permis en plus des méthodes listées : les ajouter au faux `ctx` du test (`fillRect` appelle `fill`, `strokeRect` appelle `stroke`). Si `state.whip > 0`, un arc devant lui et une ellipse au bout (`#c6d45a` pour la coque, `#7cb342` pour l’amande). Chaque noix est une ellipse de 16×10.

`drawWorld` peint un ovale vert, un intérieur crème, la fissure (trait `#d8ff9a`), les trois plateformes crème-vert, les fils `PALETTE.caramel`. La caméra : `cameraX = clamp(state.x - 640, 0, WORLD.width - 1280)`.

`coque.html` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Sousou — Dans la coque</title>
  <style>
    html, body { margin: 0; background: #143018; height: 100%; }
    canvas { display: block; margin: 0 auto; background: #3f9d34; }
  </style>
</head>
<body>
  <canvas id="jeu" width="1280" height="720"></canvas>
  <script type="module" src="coque/main.mjs"></script>
</body>
</html>
```

`coque/main.mjs` tient un `Set` des touches, appelle `navigator.getGamepads()`, fait `keysToInput` puis, si une manette est branchée, remplace par `padToInput`. Boucle `requestAnimationFrame` : un `step` par frame, puis `drawWorld` et `drawSousou`.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test coque/draw.test.mjs coque/logic.test.mjs coque/input.test.mjs`
Expected: PASS

- [ ] **Step 5: Vérifier à l’écran**

Ouvrir `coque.html`. Comparer à `art/coque/debout.jpg`, `course.jpg`, `caramel.jpg`, `tir.jpg`, `fouet.jpg`.

- Le t-shirt couvre la ceinture. Aucune peau à la taille ni sur les jambes.
- Flèche droite : il court vers la droite. Flèche gauche : vers la gauche.
- Espace : il saute. Près d’un fil, Espace tenu : il pend et les flèches le balancent. Relâcher Espace le lâche.
- J : une pistache part et sort de l’écran. Un deuxième J pendant le vol ne tire pas.
- L : le fouet part devant lui puis revient.
- Manette : bouton du bas saute, bouton de gauche tire, bouton de droite fouette.
- `index.html` s’ouvre encore comme avant.

- [ ] **Step 6: Commit**

```bash
git add coque.html coque/draw.mjs coque/draw.test.mjs coque/main.mjs
git commit -m "feat: playable shell level with drawn Sousou"
```
