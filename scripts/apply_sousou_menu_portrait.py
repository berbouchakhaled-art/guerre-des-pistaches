from pathlib import Path
html_path = Path("index.html")
html = html_path.read_text()
repls = [
    (
        "width: clamp(72px, 18vw, 112px);\n      height: clamp(72px, 18vw, 112px);",
        "width: clamp(80px, 20vw, 128px);\n      height: clamp(80px, 20vw, 128px);",
    ),
    (
        ".sousou-portrait { width: 64px; height: 64px; border-width: 3px; }",
        ".sousou-portrait { width: 72px; height: 72px; border-width: 3px; }",
    ),
    (
        ".sousou-portrait { width: 56px; height: 56px; }",
        ".sousou-portrait { width: 64px; height: 64px; }",
    ),
    (
        '            width="112"\n            height="112"',
        '            width="128"\n            height="128"',
    ),
]
html2 = html
for a, b in repls:
    if a not in html2:
        if b in html2:
            print("already:", repr(b[:48]))
            continue
        raise SystemExit(f"missing pattern: {a!r}")
    html2 = html2.replace(a, b)
html_path.write_text(html2)
print("index.html portrait sizes updated")
