"""Núcleo de pixel art: sprites desenhados em mapas de texto e uma fonte bitmap 5x7.

Tudo vira <rect> em SVG, sem fontes externas (o GitHub não carrega fontes em
SVGs usados como imagem) e sem dependências fora da biblioteca padrão.
"""
from __future__ import annotations

from collections import defaultdict
from html import escape

# --------------------------------------------------------------------------- #
# Sprites
# --------------------------------------------------------------------------- #


def _n(v: float) -> str:
    """Formata número sem casas decimais desnecessárias."""
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _runs(rows: list[str], palette: dict[str, str]):
    """Junta pixels vizinhos da mesma cor: horizontal e depois vertical."""
    per_color: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for r, line in enumerate(rows):
        c = 0
        while c < len(line):
            ch = line[c]
            if ch not in palette:
                c += 1
                continue
            start = c
            while c < len(line) and line[c] == ch:
                c += 1
            per_color[palette[ch]].append((start, r, c - start))

    merged: dict[str, list[tuple[int, int, int, int]]] = {}
    for color, runs in per_color.items():
        runs.sort(key=lambda t: (t[0], t[2], t[1]))
        out: list[tuple[int, int, int, int]] = []
        for c, r, w in runs:
            if out and out[-1][0] == c and out[-1][2] == w and out[-1][1] + out[-1][3] == r:
                lc, lr, lw, lh = out[-1]
                out[-1] = (lc, lr, lw, lh + 1)
            else:
                out.append((c, r, w, 1))
        merged[color] = out
    return merged


def sprite(rows: list[str], palette: dict[str, str], x: float = 0, y: float = 0,
           scale: float = 1, cls: str | None = None, attrs: str = "") -> str:
    """Desenha um mapa de texto. Caracteres fora da paleta são transparentes."""
    parts = []
    for color, rects in _runs(rows, palette).items():
        body = "".join(
            f'<rect x="{_n(x + c * scale)}" y="{_n(y + r * scale)}" '
            f'width="{_n(w * scale)}" height="{_n(h * scale)}"/>'
            for c, r, w, h in rects
        )
        parts.append(f'<g fill="{color}">{body}</g>')
    out = "".join(parts)
    if cls or attrs:
        cls_attr = f' class="{cls}"' if cls else ""
        out = f"<g{cls_attr}{(' ' + attrs) if attrs else ''}>{out}</g>"
    return out


def rect(x: float, y: float, w: float, h: float, fill: str, extra: str = "") -> str:
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" '
            f'fill="{fill}"{(" " + extra) if extra else ""}/>')


# --------------------------------------------------------------------------- #
# Fonte bitmap 5x7 (com área de acento)
# --------------------------------------------------------------------------- #
# Cada glifo tem 10 linhas: 0-1 acento, 2 respiro, 3-9 corpo da letra.
GLYPH_ROWS = 10
CAP_TOP = 3  # linha onde começa o corpo da letra
CAP_HEIGHT = 7

_BODY: dict[str, list[str]] = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "Ç": [".###.", "#...#", "#....", "#....", "#...#", ".###.", "..##."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", ".#", ".#", "#."],
    ":": [".", ".", "#", ".", ".", "#", "."],
    "·": [".", ".", ".", "#", ".", ".", "."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "-": ["....", "....", "....", "####", "....", "....", "...."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "=": ["....", "....", "####", "....", "####", "....", "...."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    ">": ["#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."],
    "(": [".#", "#.", "#.", "#.", "#.", "#.", ".#"],
    ")": ["#.", ".#", ".#", ".#", ".#", ".#", "#."],
    "▶": ["#...", "##..", "###.", "####", "###.", "##..", "#..."],
    "✓": [".....", "....#", "....#", "...#.", "#.#..", ".#...", "....."],
    "☕": ["..#.#..", ".#.#...", ".......", "######.", "#####.#", "######.", ".###..."],
}

_ACCENTS = {
    "~": [".##.#", "#..#."],
    "´": ["...#.", "..#.."],
    "^": ["..#..", ".#.#."],
}

_COMPOSED = {
    "Á": ("A", "´"), "Â": ("A", "^"), "Ã": ("A", "~"),
    "É": ("E", "´"), "Ê": ("E", "^"),
    "Í": ("I", "´"),
    "Ó": ("O", "´"), "Ô": ("O", "^"), "Õ": ("O", "~"),
    "Ú": ("U", "´"),
}


def _build_font() -> dict[str, list[str]]:
    font: dict[str, list[str]] = {}
    for ch, body in _BODY.items():
        w = len(body[0])
        font[ch] = ["." * w] * CAP_TOP + body
    for ch, (base, acc) in _COMPOSED.items():
        body = _BODY[base]
        font[ch] = _ACCENTS[acc] + ["." * len(body[0])] + body
    for ch, rows in font.items():
        assert len(rows) == GLYPH_ROWS, ch
        assert len({len(r) for r in rows}) == 1, ch
    return font


FONT = _build_font()


def _glyph(ch: str) -> list[str]:
    g = FONT.get(ch)
    if g is None:
        raise ValueError(f"caractere sem glifo na fonte pixel: {ch!r}")
    return g


def measure(s: str, scale: float = 1, spacing: int = 1) -> float:
    s = s.upper()
    if not s:
        return 0
    cols = sum(len(_glyph(ch)[0]) for ch in s) + spacing * (len(s) - 1)
    return cols * scale


def text(s: str, x: float, y: float, scale: float, color: str,
         spacing: int = 1, cls: str | None = None, attrs: str = "") -> str:
    """Escreve `s` com a fonte pixel. (x, y) é o topo da área de acento."""
    s = s.upper()
    rows = [""] * GLYPH_ROWS
    for i, ch in enumerate(s):
        g = _glyph(ch)
        for r in range(GLYPH_ROWS):
            rows[r] += g[r] + ("." * spacing if i < len(s) - 1 else "")
    return sprite(rows, {"#": color}, x, y, scale, cls=cls, attrs=attrs)


# --------------------------------------------------------------------------- #
# Documento SVG
# --------------------------------------------------------------------------- #

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg_doc(w: float, h: float, body: str, css: str = "", title: str = "", desc: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_n(w)}" height="{_n(h)}" '
        f'viewBox="0 0 {_n(w)} {_n(h)}" shape-rendering="crispEdges" role="img" '
        f'aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
        f"<style>{css}{REDUCED_MOTION}</style>{body}</svg>\n"
    )
