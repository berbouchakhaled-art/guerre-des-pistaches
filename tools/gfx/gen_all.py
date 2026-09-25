"""Regenerates every pixel-art asset of the game (deterministic).
Usage: python3 tools/gfx/gen_all.py   (from repo root; needs Pillow + numpy)"""
import os, sys, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'gfx')
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
import items, fx, enemies, tiles, bg, decor, font
items.build(OUT); fx.build(OUT); enemies.build(OUT); tiles.build(OUT); bg.build(OUT); decor.build(OUT); font.build(OUT)
# Sousou player sprite sheet (approved design) -> assets/sousou-sprite.png
sp = os.path.join(ROOT, 'tools', 'sousou-sprite')
subprocess.check_call([sys.executable, 'build.py'], cwd=sp)
shutil.copyfile(os.path.join(sp, 'sousou_sprite.png'), os.path.join(ROOT, 'assets', 'sousou-sprite.png'))
for f in ('sousou_sprite.png', 'sousou_sprite.json', 'sousou_sprite_preview_6x.png'):
    p = os.path.join(sp, f)
    if os.path.exists(p): os.remove(p)
print('assets written to', OUT)
