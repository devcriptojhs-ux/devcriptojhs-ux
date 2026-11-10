#!/usr/bin/env python3
"""Animação do café sobre o quadro de contribuições do GitHub.

Um barista em pixel art percorre os quadradinhos com contribuições, "bebe" cada
um deles (o quadrado esvazia) e enche uma caneca grande no fim do quadro.
Gera duas versões: coffee-contrib.svg (tema claro) e coffee-contrib-dark.svg.

Uso:
  python scripts/coffee_contrib.py --user LOGIN --out dist     # GraphQL com $GITHUB_TOKEN
  python scripts/coffee_contrib.py --user LOGIN --from-gh      # usa o `gh` logado
  python scripts/coffee_contrib.py --demo --out preview        # dados fictícios
  python scripts/coffee_contrib.py --demo-empty --out preview  # quadro vazio
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import measure, rect, sprite, svg_doc, text  # noqa: E402

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { weekday contributionLevel } }
      }
    }
  }
}
"""
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

Week = list[tuple[int, int]]  # (linha 0=domingo..6=sábado, nível 0..4)

# --------------------------------------------------------------------------- #
# Dados
# --------------------------------------------------------------------------- #


def parse_calendar(payload: dict) -> tuple[int, list[Week]]:
    if payload.get("errors"):
        raise SystemExit(f"Erro na GraphQL API: {payload['errors']}")
    user = payload["data"]["user"]
    if user is None:
        raise SystemExit("Usuário não encontrado no GitHub.")
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["weekday"], LEVELS[d["contributionLevel"]]) for d in w["contributionDays"]]
             for w in cal["weeks"]]
    return cal["totalContributions"], weeks


def fetch_api(user: str, token: str) -> tuple[int, list[Week]]:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "coffee-contrib"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return parse_calendar(json.load(resp))


def fetch_gh(user: str) -> tuple[int, list[Week]]:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={user}"],
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return parse_calendar(json.loads(out.stdout))


def demo_calendar(empty: bool, seed: int = 7) -> tuple[int, list[Week]]:
    rng = random.Random(seed)
    today = date.today()
    start = today - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # volta para o domingo
    weeks: list[Week] = []
    week: Week = []
    total = 0
    cur = start
    while cur <= today:
        row = (cur.weekday() + 1) % 7
        lvl = 0 if empty else rng.choices([0, 1, 2, 3, 4], [55, 20, 12, 8, 5])[0]
        total += [0, 1, 3, 6, 10][lvl]
        week.append((row, lvl))
        if row == 6:
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        weeks.append(week)
    return total, weeks


# --------------------------------------------------------------------------- #
# Visual
# --------------------------------------------------------------------------- #
THEMES = {
    "light": {
        "cells": ["#ebe3d6", "#d6b48c", "#b0804f", "#7f5130", "#4e2f1a"],
        "text": "#57606a", "accent": "#7f5130", "muted": "#8c959f",
        "mug": "#57606a", "mug_in": "#f6f1ea", "coffee": "#6b4226", "crema": "#c8955c",
        "steam": "#8c959f",
    },
    "dark": {
        "cells": ["#1e1915", "#4a3324", "#7a5232", "#b07a46", "#e0aa6a"],
        "text": "#c9d1d9", "accent": "#e0aa6a", "muted": "#8b949e",
        "mug": "#c9d1d9", "mug_in": "#1e1915", "coffee": "#8a5a36", "crema": "#e0aa6a",
        "steam": "#8b949e",
    },
}

CELL, GAP = 11, 3
PITCH = CELL + GAP
GX, GY = 12, 44
ROWS = 7
GRID_H = ROWS * PITCH - GAP
MUG_S = 4  # escala da caneca grande
MUG_IN = 8  # níveis de enchimento (linhas internas da caneca)

# O João: cabelo cacheado, barba, sorriso, camiseta branca e caneca preta.
BARISTA_TOP = [".h.hh.h..", ".hhhhhh..", ".hhssss..", ".hsksks..", ".ddwwdd..",
               "..dddd.ii", ".TTTTTsMM", ".TTTTT.MM", "..tttt..."]
WALK_A = BARISTA_TOP + [".PP..PP..", ".KK...KK."]
WALK_B = BARISTA_TOP + ["..PPPP...", "..KKKK..."]
SIPPING = [".h.hh.h..", ".hhhhhh..", ".hhssss..", ".hsksks..", ".dddddii.",
           "..ddddMM.", ".TTTTsMM.", ".TTTTT...", "..tttt...", "..PP.PP..", "..KK.KK.."]
BARISTA_PAL = {"h": "#3b2a20", "s": "#b5774f", "k": "#1a1a1a", "d": "#2a1d16", "w": "#ffffff",
               "T": "#eef1f5", "t": "#c9d0da", "M": "#1e1e24", "i": "#f2f2f2",
               "P": "#34466b", "K": "#8a8f98"}

MUG = [
    ".oooooooooo...",
    ".o........o...",
    ".o........oooo",
    ".o........o..o",
    ".o........o..o",
    ".o........o..o",
    ".o........oooo",
    ".o........o...",
    ".o........o...",
    "..oooooooo....",
]

STEP_SECONDS = 0.075   # tempo para andar uma casa
MIN_TRAVEL, MAX_TRAVEL = 6.0, 22.0
HOLD = 3.0             # pausa tomando café antes de recomeçar


def cell_xy(c: float, r: float) -> tuple[float, float]:
    return GX + c * PITCH, GY + r * PITCH


def walker_xy(c: float, r: float) -> tuple[float, float]:
    x, y = cell_xy(c, r)
    return x - 4, y - 9  # sprite de 22 px de altura, pés logo abaixo do quadrado


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def plan_route(weeks: list[Week]):
    """Caminho em zigue-zague pelas colunas, só pelos quadrados com café."""
    targets: list[tuple[int, int, int]] = []
    for c, week in enumerate(weeks):
        cells = sorted(((r, lvl) for r, lvl in week if lvl > 0), reverse=c % 2 == 1)
        targets += [(c, r, lvl) for r, lvl in cells]

    cols = len(weeks)
    start = (-1, targets[0][1] if targets else ROWS - 1)
    points = [start]
    dists = [0.0]
    arrivals: list[float] = []

    def go(c1: int, r1: int) -> None:
        c0, r0 = points[-1]
        if c0 != c1 and r0 != r1:  # anda em "L" para manter o visual de grade
            points.append((c1, r0))
            dists.append(dists[-1] + abs(c1 - c0))
            c0 = c1
        if (c0, r0) != (c1, r1):
            points.append((c1, r1))
            dists.append(dists[-1] + abs(c1 - c0) + abs(r1 - r0))

    for c, r, _lvl in targets:
        go(c, r)
        arrivals.append(dists[-1])
    go(cols, points[-1][1])
    go(cols, ROWS - 1)  # termina ao lado da caneca
    return targets, points, dists, arrivals


def render(total: int, weeks: list[Week], theme: str, updated: str) -> str:
    t = THEMES[theme]
    cols = len(weeks)
    grid_w = cols * PITCH - GAP
    mx = GX + grid_w + 16
    my = GY + GRID_H - len(MUG) * MUG_S
    W = mx + len(MUG[0]) * MUG_S + 12
    H = GY + GRID_H + 12 + 20 + 8

    targets, points, dists, arrivals = plan_route(weeks)
    length = dists[-1]
    travel = min(MAX_TRAVEL, max(MIN_TRAVEL, length * STEP_SECONDS))
    per_cell = travel / length
    D = travel + HOLD

    def pct(seconds: float) -> str:
        return f"{seconds / D * 100:.3f}"

    end_pct = pct(travel)
    css: list[str] = [
        f".cl{{animation-duration:{D:.2f}s;animation-iteration-count:infinite;"
        f"animation-timing-function:steps(1,end)}}",
    ]
    body: list[str] = []

    # quadrados
    target_index = {(c, r): i for i, (c, r, _l) in enumerate(targets)}
    for c, week in enumerate(weeks):
        for r, lvl in week:
            x, y = cell_xy(c, r)
            color = t["cells"][lvl]
            i = target_index.get((c, r))
            if i is None:
                body.append(rect(x, y, CELL, CELL, color))
            else:
                body.append(rect(x, y, CELL, CELL, color, f'class="cl k{i}"'))
                css.append(f"@keyframes k{i}{{0%{{fill:{color}}}{pct(arrivals[i] * per_cell)}%"
                           f"{{fill:{t['cells'][0]}}}}}.k{i}{{animation-name:k{i}}}")

    # caneca: fundo, café (sobe em degraus), contorno e vapor
    ix, iy, inner = mx + 2 * MUG_S, my + 1 * MUG_S, MUG_IN * MUG_S
    body.append(rect(ix, iy, inner, inner, t["mug_in"]))
    fill_kf = {0.0: inner}
    for k in range(1, MUG_IN + 1):
        if targets:
            idx = max(0, -(-k * len(targets) // MUG_IN) - 1)  # ceil(k/8 * n) - 1
            when = arrivals[idx] * per_cell
        else:
            when = travel * k / MUG_IN  # "café passando" mesmo sem commits
        fill_kf[when] = (MUG_IN - k) * MUG_S
    kf = "".join(f"{pct(s)}%{{transform:translateY({dy}px)}}" for s, dy in sorted(fill_kf.items()))
    css.append(f".fill{{animation:fill {D:.2f}s steps(1,end) infinite}}@keyframes fill{{{kf}}}")
    body.append(
        f'<clipPath id="mugin"><rect x="{ix}" y="{iy}" width="{inner}" height="{inner}"/></clipPath>'
        f'<g clip-path="url(#mugin)"><g class="fill" transform="translate(0,{inner})">'
        f'{rect(ix, iy, inner, inner, t["coffee"])}{rect(ix, iy, inner, MUG_S, t["crema"])}</g></g>'
    )
    body.append(sprite(MUG, {"o": t["mug"]}, mx, my, MUG_S))
    wisps = "".join(
        rect(mx + col * MUG_S, my - 12, MUG_S, 8, t["steam"], f'class="wisp w{n}"')
        for n, col in enumerate((3, 5, 7), start=1)
    )
    body.append(f'<g class="idle" opacity="0">{wisps}</g>')

    # barista
    sx, sy = walker_xy(*points[0])
    walk_kf = []
    last_pct = None
    for (c, r), d in zip(points, dists):
        p = pct(d * per_cell)
        if p == last_pct:
            continue
        x, y = walker_xy(c, r)
        walk_kf.append(f"{p}%{{transform:translate({x:g}px,{y:g}px)}}")
        last_pct = p
    ex, ey = walker_xy(*points[-1])
    walk_kf.append(f"100%{{transform:translate({ex:g}px,{ey:g}px)}}")
    css.append(f".walker{{animation:walk {D:.2f}s linear infinite}}@keyframes walk{{{''.join(walk_kf)}}}")
    body.append(
        f'<g class="walker" transform="translate({sx:g},{sy:g})">'
        f'<g class="walking"><g class="fa">{sprite(WALK_A, BARISTA_PAL, 0, 0, 2)}</g>'
        f'<g class="fb" opacity="0">{sprite(WALK_B, BARISTA_PAL, 0, 0, 2)}</g></g>'
        f'<g class="idle" opacity="0">{sprite(SIPPING, BARISTA_PAL, 0, 0, 2)}</g></g>'
    )
    css += [
        ".fa{animation:fa .32s steps(1,end) infinite}@keyframes fa{0%{opacity:1}50%{opacity:0}}",
        ".fb{animation:fb .32s steps(1,end) infinite}@keyframes fb{0%{opacity:0}50%{opacity:1}}",
        f".walking{{animation:walking {D:.2f}s steps(1,end) infinite}}"
        f"@keyframes walking{{0%{{opacity:1}}{end_pct}%{{opacity:0}}}}",
        f".idle{{animation:idle {D:.2f}s steps(1,end) infinite}}"
        f"@keyframes idle{{0%{{opacity:0}}{end_pct}%{{opacity:1}}}}",
        ".wisp{animation:wisp 2.1s linear infinite;opacity:0}.w2{animation-delay:.7s}.w3{animation-delay:1.4s}"
        "@keyframes wisp{0%{opacity:0;transform:translateY(0)}30%{opacity:.8}"
        "100%{opacity:0;transform:translateY(-14px)}}",
    ]

    # textos
    if total == 0:
        part1, part2 = "NENHUMA CONTRIBUIÇÃO AINDA · ", "CAFÉ PASSANDO..."
    elif total == 1:
        part1, part2 = "1 CONTRIBUIÇÃO NO ÚLTIMO ANO = ", "1 CAFÉ ☕"
    else:
        n = fmt_int(total)
        part1, part2 = f"{n} CONTRIBUIÇÕES NO ÚLTIMO ANO = ", f"{n} CAFÉS ☕"
    body.append(text(part1, GX, 12, 2, t["text"]))
    body.append(text(part2, GX + measure(part1, 2) + 2 * 2, 12, 2, t["accent"]))

    ly = GY + GRID_H + 12
    body.append(text(f"ATUALIZADO EM {updated}", GX, ly, 2, t["muted"]))
    lo, hi = "DESCAFEINADO", "ESPRESSO"
    legend_w = measure(lo, 2) + 8 + 5 * PITCH - GAP + 8 + measure(hi, 2)
    lx = GX + grid_w - legend_w
    body.append(text(lo, lx, ly, 2, t["muted"]))
    lx += measure(lo, 2) + 8
    for lvl in range(5):
        body.append(rect(lx + lvl * PITCH, ly + 7, CELL, CELL, t["cells"][lvl]))
    body.append(text(hi, lx + 5 * PITCH - GAP + 8, ly, 2, t["muted"]))

    return svg_doc(
        W, H, "".join(body), "".join(css),
        title="Quadro de contribuições movido a café",
        desc=f"Um barista em pixel art percorre o quadro de contribuições do GitHub bebendo um café "
             f"a cada quadradinho com contribuição e enche uma caneca. Total no último ano: {total}.",
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER"))
    ap.add_argument("--out", default="dist")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true", help="dados fictícios")
    mode.add_argument("--demo-empty", action="store_true", help="quadro sem contribuições")
    mode.add_argument("--from-gh", action="store_true", help="busca os dados com o gh CLI logado")
    args = ap.parse_args()

    if args.demo or args.demo_empty:
        total, weeks = demo_calendar(empty=args.demo_empty)
    else:
        if not args.user:
            ap.error("informe --user")
        if args.from_gh:
            total, weeks = fetch_gh(args.user)
        else:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                ap.error("defina GITHUB_TOKEN ou use --from-gh / --demo")
            total, weeks = fetch_api(args.user, token)

    brt = timezone(timedelta(hours=-3))
    updated = datetime.now(brt).strftime("%d/%m/%Y")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme, name in (("light", "coffee-contrib.svg"), ("dark", "coffee-contrib-dark.svg")):
        svg = render(total, weeks, theme, updated)
        (out / name).write_text(svg, encoding="utf-8")
        print(f"{out / name}  ({len(svg.encode()) / 1024:.1f} KB, {total} contribuições)")


if __name__ == "__main__":
    main()
