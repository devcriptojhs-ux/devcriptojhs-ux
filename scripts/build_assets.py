#!/usr/bin/env python3
"""Gera a arte estática do perfil em pixel art: banner, inventário e botão.

Uso:  python scripts/build_assets.py            (escreve em assets/)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixel  # noqa: E402
from pixel import rect, sprite, text, measure, svg_doc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Paleta base (azul do currículo + tons noturnos)
BG = "#10162b"
FRAME = "#2a3566"
FRAME_HI = "#3b4a85"
INK = "#f5f7ff"
BLUE = "#2244cc"
BLUE_LIGHT = "#7aa2ff"
MUTED = "#9aa4c7"
GREEN = "#5ee38b"
YELLOW = "#e5c07b"
SKY = "#61afef"
LEAF = "#98c379"
PINK = "#e06c75"
SLOT_BG = "#0b1022"


def panel(x: float, y: float, w: float, h: float, bg: str, frame: str, p: float = 4) -> str:
    """Retângulo com borda de 1 pixel e cantos 'arredondados' em pixel."""
    return "".join([
        rect(x + p, y, w - 2 * p, h, frame),
        rect(x, y + p, w, h - 2 * p, frame),
        rect(x + 2 * p, y + p, w - 4 * p, h - 2 * p, bg),
        rect(x + p, y + 2 * p, w - 2 * p, h - 4 * p, bg),
    ])


# --------------------------------------------------------------------------- #
# Banner
# --------------------------------------------------------------------------- #
P = 4  # tamanho do "pixel" do cenário


def u(x, y, w, h, fill, extra=""):
    """Retângulo em unidades de pixel do cenário."""
    return rect(x * P, y * P, w * P, h * P, fill, extra)


DEV = [  # o João sentado, de lado, olhando para o monitor (14x24)
    "....H.HH.H....",  # cachos
    "...HHHhHHHHH..",
    "..HHhHHHhHHHH.",
    "..HHHHHhHHHHs.",
    "..HHHHsssssss.",
    "..HHHSssssksss",  # orelha, olho, nariz
    "..HHHSsssssdd.",  # bigode
    "...HddddddwwS.",  # barba + sorriso
    "....dddddddd..",
    ".....dddddd...",
    ".....sSs......",
    "....TTTTTT....",  # camiseta branca
    "...TTTTTTTtsss",  # braço até o teclado
    "...TTTTTTT....",
    "...TTTTTTT....",
    "...TTTTTTt....",
    "...ttttttt....",
    "...PPPPPPPPP..",
    "...PPPPPPPPPP.",
    "..........PP..",
    "..........PP..",
    "..........PP..",
    "..........PP..",
    "..........KKKK",
]
DEV_PAL = {
    "H": "#2e211a", "h": "#4d3a2d", "s": "#b5774f", "S": "#94603c", "d": "#241913",
    "k": "#111111", "w": "#ffffff", "T": "#eef1f5", "t": "#c9d0da", "P": "#34466b", "K": "#8a8f98",
}

MUG = [  # caneca preta com a borda branca, igual à da foto
    "icci..",
    "mMMMMM",
    "mMMM.M",
    "mMMMMM",
    ".mMM..",
]
MUG_PAL = {"i": "#f2f2f2", "c": "#6b4226", "M": "#1e1e24", "m": "#3c3c48"}


def build_banner() -> str:
    W, H = 840, 240
    body = [panel(0, 0, W, H, BG, FRAME)]

    # chão
    body += [u(1, 52, 208, 1, "#1d2648"), u(1, 53, 208, 5, "#0b1022"), u(2, 58, 206, 1, "#0b1022")]

    # janela com céu noturno
    body += [
        u(120, 6, 26, 20, FRAME_HI), u(121, 7, 24, 18, "#070b18"),
        sprite([".mm.", "mmmm", "mmmm", ".mm."], {"m": "#f5e6a8"}, 139 * P, 9 * P, P),
    ]
    stars = [(123, 9, ""), (127, 8, "tw tw2"), (130, 12, ""), (124, 13, "tw"), (135, 18, "tw tw3"),
             (141, 21, ""), (123, 19, "tw tw2"), (128, 22, ""), (137, 23, "tw"), (143, 17, "")]
    for sx, sy, cls in stars:
        body.append(u(sx, sy, 1, 1, "#ffffff" if cls else "#9fb3ff", f'class="{cls}"' if cls else ""))
    body += [u(132, 7, 1, 18, FRAME_HI), u(121, 15, 24, 1, FRAME_HI), u(119, 26, 28, 1, "#4a5a9a")]

    # post-its na parede
    for nx, ny, c in [(150, 8, YELLOW), (154, 10, PINK), (158, 8, LEAF), (162, 10, SKY)]:
        body.append(u(nx, ny, 3, 3, c))

    # cadeira (encosto e assento atrás do personagem)
    body += [u(147, 34, 2, 13, "#3d4466"), u(148, 47, 9, 2, "#3d4466"),
             u(151, 49, 2, 2, "#2b3150"), u(148, 51, 8, 1, "#2b3150")]

    # mesa, teclado e caneca
    body += [
        u(155, 41, 53, 1, "#a8754a"), u(155, 42, 53, 1, "#7a4b2c"),
        u(161, 43, 1, 9, "#5c3920"), u(205, 43, 1, 9, "#5c3920"),
        sprite(["kKkKkKkKk"], {"k": "#cfd8e3", "K": "#8f9bb0"}, 157 * P, 40 * P, P),
        sprite(MUG, MUG_PAL, 166 * P, 36 * P, P),
    ]
    # vapor do café
    for i, (sx, sy) in enumerate([(167, 33), (169, 32), (168, 34)]):
        body.append(u(sx, sy, 1, 2, "#cfd8e3", f'class="st st{i + 1}"'))

    # monitor com mini-kanban
    body += [
        u(172, 15, 34, 22, "#2b2f3a"), u(173, 16, 32, 20, "#0d1b2a"),
        u(187, 37, 4, 3, "#2b2f3a"), u(183, 40, 12, 1, "#3b404d"),
        u(174, 17, 9, 1, YELLOW), u(184, 17, 9, 1, SKY), u(194, 17, 9, 1, LEAF),
    ]
    for cx, cy, c in [(175, 19, "#cfd8e3"), (175, 22, "#8fa0b8"), (185, 19, "#cfd8e3"),
                      (195, 19, "#8fa0b8"), (195, 22, "#8fa0b8"), (195, 25, "#8fa0b8")]:
        body.append(u(cx, cy, 7, 2, c))
    body.append(f'<g class="card">{u(175, 25, 7, 2, "#ffd479")}</g>')

    # personagem
    body.append(sprite(DEV, DEV_PAL, 146 * P, 28 * P, P))

    # textos
    tx, ty = 40, 44
    body += [
        text("JOÃO HENRIQUE", tx + 4, ty + 4, 4, BLUE),
        text("JOÃO HENRIQUE", tx, ty, 4, INK),
        text("GESTÃO DE PROJETOS · PRODUTO", tx, ty + 56, 2, BLUE_LIGHT),
        text("PROCESSOS E AUTOMAÇÃO", tx, ty + 80, 2, MUTED),
    ]
    for i in range(40):
        body.append(rect(tx + i * 8, ty + 110, 4, 4, FRAME))
    prompt = "> CAFÉ + LÓGICA = SISTEMAS"
    body.append(text(prompt, tx, ty + 122, 2, GREEN))
    body.append(rect(tx + measure(prompt, 2) + 6, ty + 128, 10, 14, GREEN, 'class="cur"'))

    css = (
        ".tw{animation:tw 3s steps(1,end) infinite}.tw2{animation-delay:-1s}.tw3{animation-delay:-2s}"
        "@keyframes tw{0%{opacity:1}50%{opacity:.2}}"
        ".card{animation:card 6s ease-in-out infinite}"
        "@keyframes card{0%,28%{transform:translate(0,0);opacity:1}"
        "36%,61%{transform:translate(40px,-12px)}"
        "69%,90%{transform:translate(80px,12px);opacity:1}"
        "96%{transform:translate(80px,12px);opacity:0}100%{transform:translate(0,0);opacity:0}}"
        ".st{opacity:0;animation:st 2.4s linear infinite}.st2{animation-delay:.8s}.st3{animation-delay:1.6s}"
        "@keyframes st{0%{opacity:0;transform:translateY(0)}25%{opacity:.85}"
        "100%{opacity:0;transform:translateY(-16px)}}"
        ".cur{animation:blink 1s steps(1,end) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}}"
    )
    return svg_doc(
        W, H, "".join(body), css,
        title="João Henrique — Gestão de Projetos, Produto e Automação",
        desc="Cena em pixel art: o João, de cabelo cacheado, barba e camiseta branca, trabalha à "
             "noite num monitor com um quadro kanban, ao lado de uma caneca preta de café fumegante.",
    )


# --------------------------------------------------------------------------- #
# Inventário
# --------------------------------------------------------------------------- #
ICONS: list[tuple[str, list[str], dict[str, str], str]] = [
    ("KANBAN", [
        "fffffffffffff",
        "fyyyfbbbfgggf",
        "fffffffffffff",
        "fwwwfdddfwwwf",
        "fwwwfdddfwwwf",
        "fdddfdddfdddf",
        "fwwwfwwwfwwwf",
        "fwwwfwwwfwwwf",
        "fdddfdddfdddf",
        "fwwwfdddfdddf",
        "fwwwfdddfdddf",
        "fffffffffffff",
    ], {"f": "#8892b0", "y": YELLOW, "b": SKY, "g": LEAF, "d": "#1b2342", "w": "#dfe6f0"},
        "FLUXO VISÍVEL E GARGALOS NA MESA."),
    ("SCRUM", [
        "....aaaa....",
        "..aa....aa..",
        ".a........a.",
        ".a.......aaa",
        "a.........a.",
        "a....ww.....",
        "a....ww.....",
        "a..........a",
        ".a........a.",
        ".a........a.",
        "..aa....aa..",
        "....aaaa....",
    ], {"a": SKY, "w": "#dfe6f0"}, "SPRINTS CURTAS, ENTREGAS DE VERDADE."),
    ("NOTION", [
        "kkkkkkkkkk",
        "kwwwwwwwwk",
        "rwllllllwk",
        "kwwwwwwwwk",
        "rwllllllwk",
        "kwwwwwwwwk",
        "rwlllllwwk",
        "kwwwwwwwwk",
        "rwlllwwwwk",
        "kwwwwwwwwk",
        "kwwwwwwwwk",
        "kkkkkkkkkk",
    ], {"k": "#8892b0", "w": "#dfe6f0", "l": "#9aa7b8", "r": YELLOW},
        "BACKLOG, ROADMAP E DOCUMENTAÇÃO."),
    ("POWER BI", [
        "a...........",
        "a........gg.",
        "a........gg.",
        "a.....bb.gg.",
        "a.....bb.gg.",
        "a.....bb.gg.",
        "a..yy.bb.gg.",
        "a..yy.bb.gg.",
        "a..yy.bb.gg.",
        "a..yy.bb.gg.",
        "a..yy.bb.gg.",
        "aaaaaaaaaaaa",
    ], {"a": "#8892b0", "y": YELLOW, "b": SKY, "g": LEAF}, "PAINÉIS QUE VIRAM DECISÃO."),
    ("BPM", [
        "...bbbbbb...",
        "...bbbbbb...",
        ".....aa.....",
        ".....dd.....",
        "....ddddaaa.",
        "....dddd..a.",
        ".....dd...a.",
        ".....aa...a.",
        ".....aa...a.",
        "...gggggg.a.",
        "...ggggggaa.",
        "............",
    ], {"b": SKY, "d": YELLOW, "g": LEAF, "a": "#8892b0"}, "PROCESSOS MAPEADOS DE PONTA A PONTA."),
    ("LEAN", [
        "tttttttttttT",
        ".ttttttttTT.",
        "..tttttttT..",
        "...ttttTT...",
        "....tttT....",
        "....tttT....",
        "....tttT....",
        ".....tT.....",
        "............",
        ".....gg.....",
        ".....gg.....",
        "............",
    ], {"t": "#56b6c2", "T": "#3e8f99", "g": LEAF}, "MENOS DESPERDÍCIO, MAIS VALOR."),
    ("ISO 9001", [
        "ssssssssssss",
        "ssssssssssss",
        "ssssssssswws",
        "sssssssswwss",
        "ssssssswwsss",
        "sswwsswwssss",
        "ssswwwssssss",
        "sssswsssssss",
        ".ssssssssss.",
        "..ssssssss..",
        "...ssssss...",
        ".....ss.....",
    ], {"s": "#6f9a52", "w": "#ffffff"}, "QUALIDADE QUE PASSA NA AUDITORIA."),
    ("APIS", [
        "...a....a...",
        "...a....a...",
        ".pppppppppP.",
        ".pppppppppP.",
        ".pppppppppP.",
        "..ppppppPP..",
        "...ppppPP...",
        "....ppPP....",
        ".....cc.....",
        ".....cc.....",
        "......cc....",
        ".......ccccc",
    ], {"a": "#cfd8e3", "p": "#d19a66", "P": "#a8794d", "c": "#8892b0"},
        "SISTEMAS CONVERSANDO ENTRE SI."),
    ("AUTOMAÇÃO", [
        "....gggg....",
        ".gg.gggg.gg.",
        ".gggggggggg.",
        "..gggggggg..",
        "ggggg..ggggg",
        "gggg....gggg",
        "gggg....gggg",
        "ggggg..ggggg",
        "..gggggggg..",
        ".gggggggggg.",
        ".gg.gggg.gg.",
        "....gggg....",
    ], {"g": "#abb2bf"}, "SE REPETE, VIRA SCRIPT."),
    ("PYTHON", [
        "tttttttttttt",
        "trtytGtttttt",
        "tbbbbbbbbbbt",
        "tbGbbbbbbbbt",
        "tbbGbbbbbbbt",
        "tbbbGbbbbbbt",
        "tbbGbbbbbbbt",
        "tbGbbbbbbbbt",
        "tbbbbbbbbbbt",
        "tbbbbbbbbbbt",
        "tbbbbbbbbbbt",
        "tttttttttttt",
    ], {"t": "#4b5577", "r": PINK, "y": YELLOW, "G": LEAF, "b": "#0d1b2a"},
        "SCRIPTS, BOTS E SIDE QUESTS."),
]


def build_inventory() -> str:
    W, H = 840, 320
    body = [panel(0, 0, W, H, BG, FRAME)]
    body.append(text("INVENTÁRIO", 32, 18, 2, INK))
    right = "ITENS EQUIPADOS"
    body.append(text(right, W - 32 - measure(right, 2), 18, 2, MUTED))

    slots = []
    for i, (label, rows, pal, _desc) in enumerate(ICONS):
        col, row = i % 5, i // 5
        cx = 116 + 152 * col
        sx, sy = cx - 32, 56 + 104 * row
        slots.append((sx, sy))
        body += [rect(sx, sy, 64, 64, FRAME), rect(sx + 4, sy + 4, 56, 56, SLOT_BG),
                 rect(sx + 4, sy + 4, 56, 4, "#18203d")]
        iw, ih = len(rows[0]) * 4, len(rows) * 4
        ix, iy = sx + (64 - iw) / 2, sy + (64 - ih) / 2
        body.append(sprite(rows, pal, ix, iy, 4))
        if label == "PYTHON":  # cursor piscando no terminal
            body.append(rect(ix + 7 * 4, iy + 7 * 4, 12, 4, "#dfe6f0", 'class="cur"'))
        body.append(text(label, cx - measure(label, 2) / 2, sy + 70, 2, "#cfd8e3"))

    # cursor de seleção que passeia pelos slots
    n = len(slots)
    step = 100 / n
    x0, y0 = slots[0]
    corners = "".join([
        rect(0, 0, 14, 4, YELLOW), rect(0, 0, 4, 14, YELLOW),
        rect(62, 0, 14, 4, YELLOW), rect(72, 0, 4, 14, YELLOW),
        rect(0, 72, 14, 4, YELLOW), rect(0, 62, 4, 14, YELLOW),
        rect(62, 72, 14, 4, YELLOW), rect(72, 62, 4, 14, YELLOW),
    ])
    body.append(f'<g class="sel" transform="translate({x0 - 6},{y0 - 6})">{corners}</g>')
    sel_kf = "".join(
        f"{i * step:.2f}%{{transform:translate({sx - 6}px,{sy - 6}px)}}" for i, (sx, sy) in enumerate(slots)
    )

    # caixa de diálogo com a descrição do item selecionado
    body += [rect(32, 264, 776, 40, FRAME), rect(36, 268, 768, 32, SLOT_BG),
             text("▶", 52, 271, 2, YELLOW)]
    desc_css = []
    for i, (_label, _rows, _pal, desc) in enumerate(ICONS):
        body.append(text(desc, 72, 271, 2, INK, cls=f"d d{i}",
                         attrs='opacity="1"' if i == 0 else 'opacity="0"'))
        if i == 0:
            desc_css.append(f"@keyframes d0{{0%{{opacity:1}}{step:.2f}%{{opacity:0}}}}")
        else:
            desc_css.append(
                f"@keyframes d{i}{{0%{{opacity:0}}{i * step:.2f}%{{opacity:1}}"
                f"{(i + 1) * step:.2f}%{{opacity:0}}}}"
            )
        desc_css.append(f".d{i}{{animation-name:d{i}}}")

    dur = n * 1.6
    css = (
        f".sel{{animation:sel {dur:.1f}s steps(1,end) infinite}}@keyframes sel{{{sel_kf}}}"
        f".d{{animation-duration:{dur:.1f}s;animation-timing-function:steps(1,end);"
        f"animation-iteration-count:infinite}}"
        + "".join(desc_css)
        + ".cur{animation:blink 1s steps(1,end) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}}"
    )
    return svg_doc(
        W, H, "".join(body), css,
        title="Inventário de ferramentas",
        desc="Inventário estilo RPG com: Kanban, Scrum, Notion, Power BI, BPM, Lean, ISO 9001, "
             "APIs, Automação e Python.",
    )


# --------------------------------------------------------------------------- #
# Botão do LinkedIn
# --------------------------------------------------------------------------- #
ADD_CONTACT = [
    "..www.....",
    ".wwwww....",
    ".wwwww..y.",
    "..www..yyy",
    "........y.",
    ".wwwww....",
    "wwwwwww...",
    "wwwwwww...",
]


def build_button() -> str:
    W, H = 340, 68
    label = "CONECTAR NO LINKEDIN"
    body = [
        panel(4, 4, 336, 64, "#0b1440", "#0b1440"),
        panel(0, 0, 336, 64, BLUE, "#0f1a4d"),
        rect(8, 8, 320, 4, "#3a62e8"),
        rect(8, 52, 320, 4, "#1a3399"),
        sprite(ADD_CONTACT, {"w": "#ffffff", "y": YELLOW}, 28, 20, 3),
        text(label, 74, 19, 2, "#ffffff"),
        '<clipPath id="btn"><rect x="4" y="4" width="328" height="56"/></clipPath>',
        '<g clip-path="url(#btn)"><g class="shine">',
        rect(0, 4, 8, 56, "#ffffff", 'opacity=".18"'),
        rect(12, 4, 4, 56, "#ffffff", 'opacity=".18"'),
        "</g></g>",
    ]
    css = (".shine{transform:translateX(-24px);animation:shine 3.5s linear infinite}"
           "@keyframes shine{0%{transform:translateX(-24px)}35%,100%{transform:translateX(340px)}}")
    return svg_doc(W, H, "".join(body), css, title="Conectar no LinkedIn",
                   desc="Botão em pixel art que leva ao perfil do LinkedIn.")


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    outputs = {
        "banner.svg": build_banner(),
        "inventory.svg": build_inventory(),
        "btn-linkedin.svg": build_button(),
    }
    for name, svg in outputs.items():
        path = ASSETS / name
        path.write_text(svg, encoding="utf-8")
        print(f"{path.relative_to(ROOT)}  ({len(svg.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
