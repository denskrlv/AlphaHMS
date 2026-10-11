"""Generate the AlphaHMS architecture figure (assets/architecture.svg).

Usage: python assets/make_architecture_figure.py [output.svg]
Uses only the Python standard library.
"""

import math
import random
import re
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/architecture.svg"
W = 1200

# ---------------------------------------------------------------- palette
INK = "#1F2328"
MUTED = "#5A6270"
RULE = "#D5DAE0"
EEG, EEG_L, EEG_M = "#2F6690", "#EAF1F7", "#A9C3D9"
SPEC, SPEC_L, SPEC_M = "#B4532A", "#FAEEE7", "#E6B39B"
FUS, FUS_L = "#5B4B8A", "#EFECF6"
CLS, CLS_L = "#2F7D53", "#E7F3EC"
REGION = {"F": "#4C78A8", "C": "#72B7B2", "P": "#54A24B", "O": "#B279A2"}
EEG_TOK = ["#2F6690", "#4A80A8", "#6D9BC0", "#93B6D3"]
SPEC_TOK = ["#B4532A", "#C76E46", "#D88D69", "#E6AE92"]

SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
SERIF = "'Times New Roman', Times, 'STIX Two Text', serif"

out = []


def add(s):
    out.append(s)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=15, anchor="start", weight="normal", fill=INK, italic=False, family=SANS, extra=""):
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
        f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{st} {extra}>{esc(s)}</text>')


def math_text(x, y, s, size=17, anchor="middle", fill=INK):
    """Tiny TeX-like markup: _x / _{..} subscripts, ^x / ^{..} superscripts, *v* italic."""
    tokens = re.findall(r"(\^\{[^}]*\}|_\{[^}]*\}|\^.|_.|\*[^*]+\*|[^_^*]+)", s)
    parts = []
    offset = 0
    small = size * 0.68
    for tok in tokens:
        if tok[0] in "^_":
            body = tok[2:-1] if tok[1] == "{" else tok[1:]
            shift = -size * 0.38 if tok[0] == "^" else size * 0.22
            dy = shift - offset
            offset = shift
            st = ""
            if len(body) > 2 and body.startswith("*") and body.endswith("*"):
                body, st = body[1:-1], ' font-style="italic"'
            parts.append(f'<tspan dy="{dy:.1f}" font-size="{small:.1f}"{st}>{esc(body)}</tspan>')
        else:
            dy = -offset
            offset = 0
            if tok.startswith("*"):
                parts.append(f'<tspan dy="{dy:.1f}" font-style="italic">{esc(tok[1:-1])}</tspan>')
            else:
                parts.append(f'<tspan dy="{dy:.1f}">{esc(tok)}</tspan>')
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SERIF}" font-size="{size}" '
        f'text-anchor="{anchor}" fill="{fill}">{"".join(parts)}</text>')


def rect(x, y, w, h, fill="none", stroke=INK, sw=1.2, rx=0, extra=""):
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=1.2, extra=""):
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
        f'stroke-width="{sw}" {extra}/>')


def arrow(x1, y1, x2, y2, color=INK, sw=1.4, extra=""):
    mid = {INK: "a-ink", EEG: "a-eeg", SPEC: "a-spec", FUS: "a-fus", CLS: "a-cls", MUTED: "a-muted"}[color]
    line(x1, y1, x2, y2, color, sw, f'marker-end="url(#{mid})" {extra}')


def curve(d, color=INK, sw=1.4, head=True, extra=""):
    mid = {INK: "a-ink", EEG: "a-eeg", SPEC: "a-spec", FUS: "a-fus", CLS: "a-cls", MUTED: "a-muted"}[color]
    me = f'marker-end="url(#{mid})"' if head else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" {me} {extra}/>')


def circle(x, y, r, fill, stroke="none", sw=1.0, extra=""):
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def header(y, tag, title):
    text(50, y, tag, 19, weight="bold")
    text(82, y, title, 19, weight="bold")
    line(50, y + 11, 1150, y + 11, RULE, 1)


def box(x, y, w, h, title, lines, color, fill, title_size=16):
    rect(x, y, w, h, fill, color, 1.4, rx=8)
    cy = y + 24
    text(x + w / 2, cy, title, title_size, "middle", "bold", color)
    for i, ln in enumerate(lines):
        text(x + w / 2, cy + 21 * (i + 1), ln, 13.5, "middle", fill=MUTED)


# ---------------------------------------------------------------- 10-20 layout
def polar(deg, r=0.80):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


POS = {
    "Fp1": polar(108), "Fp2": polar(72), "F7": polar(144), "F8": polar(36),
    "T3": polar(180), "T4": polar(0), "T5": polar(216), "T6": polar(324),
    "O1": polar(252), "O2": polar(288),
    "Fz": (0, 0.40), "Cz": (0, 0), "Pz": (0, -0.40),
    "C3": (-0.40, 0), "C4": (0.40, 0),
    "F3": (-0.33, 0.43), "F4": (0.33, 0.43), "P3": (-0.33, -0.43), "P4": (0.33, -0.43),
}
CH_REGION = {
    "Fp1": "F", "Fp2": "F", "F3": "F", "F4": "F", "F7": "F", "F8": "F", "Fz": "F",
    "C3": "C", "C4": "C", "Cz": "C", "T3": "C", "T4": "C",
    "P3": "P", "P4": "P", "Pz": "P", "T5": "P", "T6": "P",
    "O1": "O", "O2": "O",
}
ADJ = {
    'Fp1': ['F7', 'F3', 'Fp2'], 'Fp2': ['Fp1', 'F4', 'F8'], 'F7': ['Fp1', 'F3', 'T3'],
    'F3': ['Fp1', 'F7', 'Fz', 'C3'], 'Fz': ['F3', 'F4', 'Cz'], 'F4': ['Fp2', 'Fz', 'F8', 'C4'],
    'F8': ['Fp2', 'F4', 'T4'], 'T3': ['F7', 'C3', 'T5'], 'C3': ['F3', 'T3', 'Cz', 'P3'],
    'Cz': ['Fz', 'C3', 'C4', 'Pz'], 'C4': ['F4', 'Cz', 'T4', 'P4'], 'T4': ['F8', 'C4', 'T6'],
    'T5': ['T3', 'P3', 'O1'], 'P3': ['C3', 'T5', 'Pz', 'O1'], 'Pz': ['Cz', 'P3', 'P4'],
    'P4': ['C4', 'Pz', 'T6', 'O2'], 'T6': ['T4', 'P4', 'O2'], 'O1': ['T5', 'P3', 'O2'],
    'O2': ['P4', 'T6', 'O1'],
}
CHAINS = {
    "LL": ["Fp1", "F7", "T3", "T5", "O1"],
    "LP": ["Fp1", "F3", "C3", "P3", "O1"],
    "RP": ["Fp2", "F4", "C4", "P4", "O2"],
    "RL": ["Fp2", "F8", "T4", "T6", "O2"],
}


def head_outline(cx, cy, R, fill="#FFFFFF", stroke=INK, sw=1.6):
    # ears + nose behind the scalp circle
    add(f'<ellipse cx="{cx - R * 1.0:.1f}" cy="{cy:.1f}" rx="{R * 0.07:.1f}" ry="{R * 0.19:.1f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    add(f'<ellipse cx="{cx + R * 1.0:.1f}" cy="{cy:.1f}" rx="{R * 0.07:.1f}" ry="{R * 0.19:.1f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    add(f'<path d="M{cx - R * 0.13:.1f},{cy - R * 0.985:.1f} L{cx:.1f},{cy - R * 1.13:.1f} '
        f'L{cx + R * 0.13:.1f},{cy - R * 0.985:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linejoin="round"/>')
    circle(cx, cy, R, fill, stroke, sw)


def xy(ch, cx, cy, R):
    x, y = POS[ch]
    return cx + R * x, cy - R * y


def brain(cx, cy, R):
    """Stylised top view of the cortex: two hemispheres with a few sulci."""
    for side in (-1, 1):
        hx = cx + side * R * 0.43
        add(f'<ellipse cx="{hx:.1f}" cy="{cy + R * 0.02:.1f}" rx="{R * 0.40:.1f}" ry="{R * 0.86:.1f}" '
            f'fill="#F6EEEC" stroke="#DCC7C2" stroke-width="1.4"/>')
        sulci = [
            [(0.08, 0.05), (0.30, 0.18), (0.55, 0.02), (0.74, 0.10)],   # central sulcus
            [(0.10, 0.48), (0.28, 0.40), (0.42, 0.58), (0.66, 0.46)],
            [(0.12, 0.72), (0.30, 0.66), (0.44, 0.78), (0.60, 0.70)],
            [(0.10, -0.30), (0.30, -0.20), (0.50, -0.38), (0.74, -0.26)],
            [(0.12, -0.58), (0.30, -0.66), (0.46, -0.52), (0.62, -0.62)],
            [(0.52, 0.30), (0.64, 0.22), (0.70, 0.36), (0.78, 0.30)],
            [(0.50, -0.10), (0.62, -0.02), (0.68, -0.16), (0.80, -0.08)],
        ]
        for pts in sulci:
            p = [(cx + side * R * px, cy - R * py) for px, py in pts]
            add(f'<path d="M{p[0][0]:.1f},{p[0][1]:.1f} C{p[1][0]:.1f},{p[1][1]:.1f} '
                f'{p[2][0]:.1f},{p[2][1]:.1f} {p[3][0]:.1f},{p[3][1]:.1f}" fill="none" '
                f'stroke="#DCC7C2" stroke-width="1.5" stroke-linecap="round"/>')


# ---------------------------------------------------------------- colormap
VIRIDIS = [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)]


def cmap(v):
    v = min(max(v, 0.0), 1.0) * (len(VIRIDIS) - 1)
    i = min(int(v), len(VIRIDIS) - 2)
    t = v - i
    a, b = VIRIDIS[i], VIRIDIS[i + 1]
    return "#%02x%02x%02x" % tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))


rng = random.Random(7)

# =================================================================== (a)
header(40, "(a)", "Acquisition")
HCX, HCY, HR = 600, 215, 132
head_outline(HCX, HCY, HR)
brain(HCX, HCY, HR)
for name, chain in CHAINS.items():
    pts = " ".join(f"{xy(c, HCX, HCY, HR)[0]:.1f},{xy(c, HCX, HCY, HR)[1]:.1f}" for c in chain)
    add(f'<polyline points="{pts}" fill="none" stroke="{SPEC}" stroke-width="2" '
        f'stroke-dasharray="5 4" stroke-opacity="0.75" stroke-linejoin="round"/>')
for ch in POS:
    x, y = xy(ch, HCX, HCY, HR)
    circle(x, y, 11.5, REGION[CH_REGION[ch]], "#FFFFFF", 1.6)
    text(x, y + 3.6, ch, 9.5, "middle", "bold", "#FFFFFF")
text(HCX, HCY + HR + 30, "19-channel scalp EEG · 10–20 system · 200 Hz", 14, "middle", fill=MUTED)

# left legend: clinical regions
lx, ly = 60, 108
text(lx, ly, "Clinical regions", 15, weight="bold")
text(lx, ly + 19, "electrode colour; used for regional pooling", 12.5, fill=MUTED)
for i, (k, name, n) in enumerate([("F", "Frontal", 7), ("C", "Central", 5), ("P", "Parietal", 5), ("O", "Occipital", 2)]):
    yy = ly + 48 + i * 26
    circle(lx + 9, yy - 5, 8, REGION[k])
    text(lx + 26, yy, f"{name}", 14.5)
    text(lx + 120, yy, f"{n} ch", 13.5, fill=MUTED)

# right legend: montage chains
rx_, ry_ = 850, 108
text(rx_, ry_, "Bipolar montage chains", 15, weight="bold")
text(rx_, ry_ + 19, "source of the provided spectrograms", 12.5, fill=MUTED)
for i, (name, chain) in enumerate(CHAINS.items()):
    yy = ry_ + 48 + i * 26
    line(rx_, yy - 5, rx_ + 22, yy - 5, SPEC, 2, 'stroke-dasharray="5 4"')
    text(rx_ + 30, yy, name, 14.5, weight="bold", fill=SPEC)
    text(rx_ + 60, yy, "–".join(chain), 13.5, fill=MUTED)

# fork into two branches
BR_Y = 420
curve(f"M{HCX - 30},{HCY + HR + 40} C{HCX - 30},{BR_Y - 6} 310,{BR_Y - 34} 310,{BR_Y - 4}", EEG, 1.8)
curve(f"M{HCX + 30},{HCY + HR + 40} C{HCX + 30},{BR_Y - 6} 890,{BR_Y - 34} 890,{BR_Y - 4}", SPEC, 1.8)
text(440, BR_Y + 30, "raw signals", 13, "start", fill=EEG, italic=True)
text(760, BR_Y + 30, "spectrograms", 13, "end", fill=SPEC, italic=True)
for cx, label, c, cl in [(310, "EEG branch", EEG, EEG_L), (890, "Spectrogram branch", SPEC, SPEC_L)]:
    rect(cx - 110, BR_Y, 220, 34, cl, c, 1.4, rx=17)
    text(cx, BR_Y + 23, label, 16, "middle", "bold", c)

# =================================================================== (b)
Y_B = 500
header(Y_B, "(b)", "Preprocessing & temporal windowing")

# --- EEG traces
PX0, PX1, PT, PB = 100, 550, Y_B + 32, Y_B + 172
sx = (PX1 - PX0) / 50.0
rect(PX0 + 20 * sx, PT - 4, 10 * sx, PB - PT + 8, EEG_L, "none", 0)
n_ch = 19
sp = (PB - PT) / n_ch
order = ["Fp1", "F3", "C3", "P3", "F7", "T3", "T5", "O1", "Fz", "Cz", "Pz",
         "Fp2", "F4", "C4", "P4", "F8", "T4", "T6", "O2"]
for c in range(n_ch):
    y0 = PT + (c + 0.5) * sp
    comps = [(rng.uniform(0.05, 0.12), rng.uniform(0, 6.28), rng.uniform(0.4, 1.0)),
             (rng.uniform(0.25, 0.45), rng.uniform(0, 6.28), rng.uniform(0.2, 0.5)),
             (rng.uniform(0.7, 1.2), rng.uniform(0, 6.28), rng.uniform(0.1, 0.3))]
    pts = []
    for i in range(int(PX1 - PX0) + 1):
        t = i
        v = sum(a * math.sin(f * t + p) for f, p, a in comps) + rng.gauss(0, 0.12)
        sec = t / sx
        if 20 <= sec <= 30 and order[c] in ("Fp1", "F3", "C3", "F7", "T3"):
            ph = (sec - 20) % 1.6
            v += 1.6 * math.exp(-((ph - 0.3) ** 2) / 0.006)
        pts.append(f"{PX0 + t:.1f},{y0 - v * sp * 0.38:.1f}")
    add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#3B4250" stroke-width="0.7"/>')
text(PX0 - 6, PT + sp * 0.5 + 4, "Fp1", 11, "end", fill=MUTED)
text(PX0 - 6, (PT + PB) / 2 + 4, "⋮", 13, "end", fill=MUTED)
text(PX0 - 6, PB - sp * 0.5 + 4, "O2", 11, "end", fill=MUTED)
# windows (two lanes)
for w in range(9):
    lane = w % 2
    yy = PB + 12 + lane * 8
    x0 = PX0 + 5 * w * sx + 1.5
    x1 = PX0 + (5 * w + 10) * sx - 1.5
    col = EEG if w == 4 else EEG_M
    line(x0, yy, x1, yy, col, 4 if w == 4 else 3, 'stroke-linecap="round"')
for s in range(0, 51, 10):
    xx = PX0 + s * sx
    line(xx, PB + 30, xx, PB + 34, MUTED, 1)
    text(xx, PB + 47, f"{s}", 11.5, "middle", fill=MUTED)
text(PX1, PB + 47, "s", 11.5, "start", fill=MUTED, extra='dx="12"')
text(PX0 + 25 * sx, PT - 9, "labelled window", 12, "middle", fill=EEG, italic=True)
text(310, PB + 72, "band-pass 0.5–50 Hz · notch 60 Hz · z-score", 13.5, "middle", fill=MUTED)
text(310, PB + 92, "50 s → 9 windows of 10 s (stride 5 s)", 13.5, "middle", weight="bold", fill=EEG)

# --- Spectrogram heatmap
SX0, SX1 = 680, 1130
ssx = (SX1 - SX0) / 600.0
strip_h, gap = 30, 5
names = ["LL", "RL", "LP", "RP"]
tb, fb = 60, 7
for r, name in enumerate(names):
    y0 = PT + r * (strip_h + gap)
    phase = rng.uniform(0, 6.28)
    for ti in range(tb):
        for fi in range(fb):
            base = 0.85 - 0.09 * fi
            mod = 0.12 * math.sin(ti * 0.16 + phase) + 0.08 * math.sin(ti * 0.53 + phase * 2)
            burst = 0.18 if 40 <= ti <= 49 and fi < 4 else 0.0
            v = base + mod + burst + rng.gauss(0, 0.06)
            cw = (SX1 - SX0) / tb
            ch_ = strip_h / fb
            rect(SX0 + ti * cw, y0 + strip_h - (fi + 1) * ch_, cw + 0.4, ch_ + 0.4, cmap(v), "none", 0)
    text(SX0 - 6, y0 + strip_h / 2 + 4, name, 12, "end", "bold", SPEC)
c0 = SX0 + 295 * ssx
rect(c0 - 1, PT - 3, 10 * ssx + 2, 4 * strip_h + 3 * gap + 6, "none", "#FFFFFF", 1.6)
text(c0 + 5 * ssx, PT - 9, "labelled window", 12, "middle", fill=SPEC, italic=True)
# 119 windows comb
for w in range(119):
    xx = SX0 + (5 * w + 5) * ssx
    col = SPEC if w == 59 else SPEC_M
    line(xx, PB + 12, xx, PB + 22, col, 2 if w == 59 else 0.9)
for s in range(0, 601, 100):
    xx = SX0 + s * ssx
    line(xx, PB + 30, xx, PB + 34, MUTED, 1)
    text(xx, PB + 47, f"{s}", 11.5, "middle", fill=MUTED)
text(SX1, PB + 47, "s", 11.5, "start", fill=MUTED, extra='dx="14"')
text(SX1 + 8, PT + 10, "20 Hz", 10.5, fill=MUTED)
text(SX1 + 8, PT + strip_h, "0", 10.5, fill=MUTED)
text(890, PB + 72, "clip [10⁻², 10⁶] → log → normalise", 13.5, "middle", fill=MUTED)
text(890, PB + 92, "600 s → 119 windows of 10 s (stride 5 s)", 13.5, "middle", weight="bold", fill=SPEC)

# =================================================================== (c)
Y_C = 800
header(Y_C, "(c)", "Graph construction (one graph per window)")


def stack(cx, cy, R, n_back, color):
    for k in range(n_back, 0, -1):
        circle(cx + 9 * k, cy - 9 * k, R, "#FFFFFF", color, 1.1, 'stroke-opacity="0.45"')


# EEG graph
GCX, GCY, GR = 175, Y_C + 124, 80
stack(GCX, GCY, GR, 2, EEG)
circle(GCX, GCY, GR, "#FFFFFF", EEG, 1.4)
seen = set()
for a, nbrs in ADJ.items():
    for b in nbrs:
        if (b, a) in seen:
            continue
        seen.add((a, b))
        x1, y1 = xy(a, GCX, GCY, GR)
        x2, y2 = xy(b, GCX, GCY, GR)
        line(x1, y1, x2, y2, "#7D8896", 1.1)
for ch in POS:
    x, y = xy(ch, GCX, GCY, GR)
    circle(x, y, 5.5, REGION[CH_REGION[ch]], "#FFFFFF", 1.2)
text(GCX, GCY + GR + 26, "𝒢₁ … 𝒢₉", 15, "middle", fill=EEG, family=SERIF, italic=True)

tx = 300
text(tx, Y_C + 48, "Nodes", 14, weight="bold")
text(tx + 62, Y_C + 48, "19 electrodes", 14, fill=MUTED)
text(tx, Y_C + 74, "Features", 14, weight="bold")
text(tx + 62, Y_C + 74, "Welch PSD per band", 14, fill=MUTED)
# mini PSD bars
bands = ["δ", "θ", "α", "β", "γ"]
vals = [0.95, 0.6, 0.45, 0.28, 0.14]
for i, (b, v) in enumerate(zip(bands, vals)):
    bx = tx + 64 + i * 22
    rect(bx, Y_C + 124 - 34 * v, 14, 34 * v, EEG_M, EEG, 1)
    text(bx + 7, Y_C + 140, b, 13, "middle", fill=INK, family=SERIF, italic=True)
math_text(tx + 225, Y_C + 112, "*X*_{*t*} ∈ ℝ^{19×5}", 17)
text(tx, Y_C + 170, "Edges", 14, weight="bold")
text(tx + 62, Y_C + 170, "10–20 neighbours", 14, fill=MUTED)
text(tx + 62, Y_C + 190, "64 directed, unweighted", 14, fill=MUTED)

# Spectrogram graph
SCX, SCY, SR = 755, Y_C + 124, 80
stack(SCX, SCY, SR, 2, SPEC)
circle(SCX, SCY, SR, "#FFFFFF", SPEC, 1.4)
spos = {"LL": (-0.62, 0.0), "LP": (-0.22, 0.0), "RP": (0.22, 0.0), "RL": (0.62, 0.0)}
sp_xy = {k: (SCX + SR * v[0], SCY - SR * v[1]) for k, v in spos.items()}
for a, b in [("LL", "LP"), ("LP", "RP"), ("RP", "RL")]:
    line(*sp_xy[a], *sp_xy[b], "#7D8896", 1.4)
x1, y1 = sp_xy["LL"]
x2, y2 = sp_xy["RL"]
add(f'<path d="M{x1:.1f},{y1:.1f} Q{SCX:.1f},{SCY - SR * 0.95:.1f} {x2:.1f},{y2:.1f}" fill="none" '
    f'stroke="#7D8896" stroke-width="1.4"/>')
for i, (k, (x, y)) in enumerate(sp_xy.items()):
    circle(x, y, 13, SPEC_TOK[i], "#FFFFFF", 1.5)
    text(x, y + 3.8, k, 10, "middle", "bold", "#FFFFFF")
text(SCX, SCY + SR + 26, "𝒢₁ … 𝒢₁₁₉", 15, "middle", fill=SPEC, family=SERIF, italic=True)

tx = 880
text(tx, Y_C + 48, "Nodes", 14, weight="bold")
text(tx + 62, Y_C + 48, "4 montage regions", 14, fill=MUTED)
text(tx, Y_C + 74, "Features", 14, weight="bold")
text(tx + 62, Y_C + 74, "mean band power ≤ 20 Hz", 14, fill=MUTED)
vals = [0.95, 0.62, 0.42, 0.25]
for i, (b, v) in enumerate(zip(bands[:4], vals)):
    bx = tx + 64 + i * 22
    rect(bx, Y_C + 124 - 34 * v, 14, 34 * v, SPEC_M, SPEC, 1)
    text(bx + 7, Y_C + 140, b, 13, "middle", fill=INK, family=SERIF, italic=True)
math_text(tx + 205, Y_C + 112, "*X*_{*t*} ∈ ℝ^{4×4}", 17)
text(tx, Y_C + 170, "Edges", 14, weight="bold")
text(tx + 62, Y_C + 170, "fixed spatial layout", 14, fill=MUTED)
text(tx + 62, Y_C + 190, "8 directed", 14, fill=MUTED)

# =================================================================== (d)
Y_D = Y_C + 274
header(Y_D, "(d)", "Spatial graph encoder & regional pooling")

BY = Y_D + 32
box(60, BY, 250, 102, "GATv2 encoder", ["2 layers · 4 heads · 64-d", "LayerNorm · ELU · dropout", "shared across all 9 windows"], EEG, EEG_L)
box(640, BY, 250, 102, "GATv2 encoder", ["2 layers · 4 heads · 64-d", "LayerNorm · ELU · dropout", "shared across all 119 windows"], SPEC, SPEC_L)

# EEG pooling: 19 dots grouped -> 4 region tokens
arrow(312, BY + 51, 338, BY + 51, EEG)
counts = [("F", 7), ("C", 5), ("P", 5), ("O", 2)]
gx = 348
for i, (k, n) in enumerate(counts):
    yy = BY + 8 + i * 25
    for j in range(n):
        circle(gx + 6 + j * 11, yy + 8, 4.2, REGION[k])
    arrow(gx + 82, yy + 8, gx + 118, yy + 8, MUTED, 1.1)
    rect(gx + 124, yy - 1, 50, 18, REGION[k], "none", 0, rx=3)
    text(gx + 149, yy + 12, {"F": "Front.", "C": "Cent.", "P": "Pariet.", "O": "Occip."}[k], 10.5, "middle", "bold", "#FFFFFF")
text(gx + 100, BY - 6, "mean", 11.5, "middle", fill=MUTED, italic=True)
math_text(gx + 41, BY + 122, "*H*_{*t*} ∈ ℝ^{19×64}", 16, fill=MUTED)
math_text(gx + 150, BY + 122, "ℝ^{4×64}", 16, fill=MUTED)

# Spec: identity regions
arrow(892, BY + 51, 918, BY + 51, SPEC)
for i, k in enumerate(["LL", "RL", "LP", "RP"]):
    yy = BY + 8 + i * 25
    circle(940, yy + 8, 6, SPEC_TOK[i])
    arrow(952, yy + 8, 1012, yy + 8, MUTED, 1.1)
    rect(1018, yy - 1, 50, 18, SPEC_TOK[i], "none", 0, rx=3)
    text(1043, yy + 12, k, 10.5, "middle", "bold", "#FFFFFF")
text(982, BY - 6, "identity", 11.5, "middle", fill=MUTED, italic=True)
math_text(940, BY + 122, "*H*_{*t*} ∈ ℝ^{4×64}", 16, fill=MUTED)
math_text(1043, BY + 122, "ℝ^{4×64}", 16, fill=MUTED)

# =================================================================== (e)
Y_E = Y_D + 192
header(Y_E, "(e)", "Temporal encoder (BiLSTM + centre-weighted attention)")


def temporal(x0, labels, center, color, light, mid, tok_cols, steps_label):
    cw, cg = 34, 8
    cy = Y_E + 92
    xs = []
    x = x0
    for lab in labels:
        if lab == "…":
            text(x + 8, cy + 22, "…", 18, "middle", fill=MUTED)
            xs.append(None)
            x += 16 + cg
            continue
        xs.append(x)
        hl = lab == center
        rect(x, cy, cw, 34, color if hl else light, color, 1.3, rx=5)
        text(x + cw / 2, cy + 22, "LSTM", 9, "middle", "bold", "#FFFFFF" if hl else color)
        math_text(x + cw / 2, cy + 56, f"*t*={lab}", 12.5, fill=MUTED)
        # attention bar above
        h = 30 if hl else rng.uniform(6, 16)
        rect(x + 9, cy - 12 - h, cw - 18, h, mid if not hl else color, "none", 0)
        x += cw + cg
    # bidirectional arrows between consecutive cells
    real = [v for v in xs if v is not None]
    for a, b in zip(real, real[1:]):
        if b - a > cw + cg + 1:
            continue
        arrow(a + cw + 1, cy + 10, b - 1, cy + 10, color, 1)
        arrow(b - 1, cy + 24, a + cw + 1, cy + 24, color, 1)
    text(x0, Y_E + 36, "attention", 11.5, fill=MUTED, italic=True)
    math_text(x0 + 52, Y_E + 36, "*α*_{*t*}", 14, anchor="start", fill=MUTED)
    text(x0 + 70, Y_E + 36, "(+0.3 bias on labelled window)", 11.5, fill=MUTED, italic=True)
    end = x - cg
    # sum node
    sx_ = end + 34
    arrow(end + 4, cy + 17, sx_ - 15, cy + 17, color, 1.2)
    circle(sx_, cy + 17, 14, "#FFFFFF", color, 1.4)
    text(sx_, cy + 23, "Σ", 16, "middle", fill=color)
    math_text(sx_, cy - 8, "ℝ^{256}", 13, fill=MUTED)
    arrow(sx_ + 15, cy + 17, sx_ + 40, cy + 17, color, 1.2)
    # projected regional tokens
    tx0 = sx_ + 46
    for i in range(4):
        rect(tx0 + i * 20, cy + 1, 16, 32, tok_cols[i], "none", 0, rx=3)
    math_text(tx0 + 38, cy + 56, "ℝ^{4×256}", 13, fill=MUTED)
    text(tx0 + 38, cy - 8, "linear", 11.5, "middle", fill=MUTED, italic=True)
    return tx0 + 38, cy + 33


e_out = temporal(62, [str(i) for i in range(1, 10)], "5", EEG, EEG_L, EEG_M, EEG_TOK, "9")
s_out = temporal(642, ["1", "2", "3", "…", "60", "…", "118", "119"], "60", SPEC, SPEC_L, SPEC_M, SPEC_TOK, "119")
text(310, Y_E + 196, "2-layer BiLSTM (128 × 2) over T = 9 windows", 13.5, "middle", fill=MUTED)
text(890, Y_E + 196, "2-layer BiLSTM (128 × 2) over T = 119 windows", 13.5, "middle", fill=MUTED)

# =================================================================== (f)
Y_F = Y_E + 226
header(Y_F, "(f)", "Regional cross-modal attention fusion")
TY = Y_F + 74
eeg_tok_x = [235 + i * 40 for i in range(4)]
spec_tok_x = [815 + i * 40 for i in range(4)]
curve(f"M{e_out[0]:.1f},{e_out[1] + 30:.1f} L{e_out[0]:.1f},{Y_F + 26} C{e_out[0]:.1f},{TY - 18} 310,{TY - 30} 310,{TY - 4}", EEG, 1.4)
curve(f"M{s_out[0]:.1f},{s_out[1] + 30:.1f} L{s_out[0]:.1f},{Y_F + 26} C{s_out[0]:.1f},{TY - 18} 890,{TY - 30} 890,{TY - 4}", SPEC, 1.4)
for i, x in enumerate(eeg_tok_x):
    rect(x, TY, 32, 32, EEG_TOK[i], "none", 0, rx=4)
    math_text(x + 16, TY + 21, f"*e*_{i + 1}", 15, fill="#FFFFFF")
for i, x in enumerate(spec_tok_x):
    rect(x, TY, 32, 32, SPEC_TOK[i], "none", 0, rx=4)
    math_text(x + 16, TY + 21, f"*s*_{i + 1}", 15, fill="#FFFFFF")
text(190, TY + 22, "EEG", 13.5, "end", "bold", EEG)
text(988, TY + 22, "Spectrogram", 13.5, "start", "bold", SPEC)

AY = TY + 96
box(170, AY, 280, 74, "EEG → Spec attention", ["Q: EEG · K, V: Spectrogram"], FUS, FUS_L, 15)
box(750, AY, 280, 74, "Spec → EEG attention", ["Q: Spectrogram · K, V: EEG"], FUS, FUS_L, 15)
text(600, AY + 30, "multi-head, 8 heads, d = 256", 13.5, "middle", fill=MUTED)
text(600, AY + 50, "residual + LayerNorm", 13.5, "middle", fill=MUTED)
# Q (straight) and K,V (crossing) arrows
arrow(310, TY + 34, 310, AY - 3, EEG, 1.5)
arrow(890, TY + 34, 890, AY - 3, SPEC, 1.5)
curve(f"M{spec_tok_x[0] - 6},{TY + 30} C700,{TY + 66} 470,{TY + 58} 410,{AY - 3}", SPEC, 1.3, extra='stroke-dasharray="5 3"')
curve(f"M{eeg_tok_x[-1] + 38},{TY + 30} C500,{TY + 66} 730,{TY + 58} 790,{AY - 3}", EEG, 1.3, extra='stroke-dasharray="5 3"')
text(300, TY + 64, "Q", 13, "end", "bold", EEG, family=SERIF, italic=True)
text(900, TY + 64, "Q", 13, "start", "bold", SPEC, family=SERIF, italic=True)
text(600, TY + 52, "K, V", 13, "middle", "bold", MUTED, family=SERIF, italic=True)

# concat per region
CY_ = AY + 120
cat_x = [452 + i * 78 for i in range(4)]
curve(f"M310,{AY + 76} C310,{CY_ - 20} 430,{CY_ - 24} {cat_x[0] - 6},{CY_ + 14}", FUS, 1.4)
curve(f"M890,{AY + 76} C890,{CY_ - 20} 770,{CY_ - 24} {cat_x[-1] + 70},{CY_ + 14}", FUS, 1.4)
for i, x in enumerate(cat_x):
    rect(x, CY_, 32, 28, EEG_TOK[i], "none", 0, rx=0)
    rect(x + 32, CY_, 32, 28, SPEC_TOK[i], "none", 0, rx=0)
    rect(x, CY_, 64, 28, "none", "#FFFFFF", 1, rx=3)
text(600, CY_ - 12, "concatenate per region", 12.5, "middle", fill=MUTED, italic=True)
math_text(cat_x[-1] + 100, CY_ + 20, "ℝ^{4×512}", 15, anchor="start", fill=MUTED)
# attention pooling
PY_ = CY_ + 80
for i, x in enumerate(cat_x):
    curve(f"M{x + 32},{CY_ + 30} C{x + 32},{PY_ - 30} 600,{PY_ - 36} 600,{PY_ - 18}", FUS, 1.1, head=(i == 1))
circle(600, PY_ - 2, 15, "#FFFFFF", FUS, 1.4)
text(600, PY_ + 4, "Σ", 16, "middle", fill=FUS)
text(745, PY_ - 26, "attention pooling over regions", 12.5, "start", fill=MUTED, italic=True)
math_text(745, PY_ - 2, "*β*_{*r*} = softmax(*w*^⊤ tanh(*W* *z*_{*r*}))", 15, anchor="start", fill=MUTED)
arrow(600, PY_ + 14, 600, PY_ + 40, FUS)
rect(536, PY_ + 44, 128, 22, FUS_L, FUS, 1.3, rx=4)
math_text(600, PY_ + 60, "*f* ∈ ℝ^{512}", 15, fill=FUS)

# =================================================================== (g)
Y_G = PY_ + 116
header(Y_G, "(g)", "Classification & training objective")
arrow(600, PY_ + 68, 600, Y_G - 14, FUS)
GY = Y_G + 34
box(80, GY + 6, 290, 112, "MLP classifier", ["512 → 256 → 128 → 6", "LayerNorm · ELU · dropout 0.3", "softmax"], CLS, CLS_L)
arrow(372, GY + 62, 432, GY + 62, CLS)

classes = ["Seizure", "LPD", "GPD", "LRDA", "GRDA", "Other"]
pred = [0.62, 0.17, 0.05, 0.08, 0.03, 0.05]
targ = [0.67, 0.13, 0.00, 0.13, 0.00, 0.07]
bx0, bw = 530, 250
for i, (c, p, t) in enumerate(zip(classes, pred, targ)):
    yy = GY + 4 + i * 20
    text(bx0 - 10, yy + 12, c, 13, "end", fill=INK)
    rect(bx0, yy + 1, bw * p, 7.5, CLS, "none", 0)
    rect(bx0, yy + 9.5, max(bw * t, 1.5), 7.5, "#B9C0C8", "none", 0)
line(bx0, GY, bx0, GY + 126, INK, 1)
# legend
lgx = 840
rect(lgx, GY + 14, 14, 9, CLS, "none", 0)
text(lgx + 22, GY + 23, "prediction", 13, fill=INK)
math_text(lgx + 102, GY + 23, "*p̂*", 15, anchor="start")
rect(lgx, GY + 38, 14, 9, "#B9C0C8", "none", 0)
text(lgx + 22, GY + 47, "expert-vote distribution", 13, fill=INK)
math_text(lgx + 178, GY + 47, "*y*", 15, anchor="start")
rect(lgx - 8, GY + 70, 318, 48, "#FFFFFF", CLS, 1.3, rx=6)
math_text(lgx + 151, GY + 101, "ℒ = KL( *y* ‖ *p̂* )", 18, fill=CLS)

H = GY + 150
svg_head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" '
            f'role="img" aria-labelledby="title desc">\n'
            '<title id="title">AlphaHMS architecture</title>\n'
            '<desc id="desc">Scalp EEG and montage spectrograms are windowed, converted to temporal graph '
            'sequences, encoded with GATv2, pooled into regions, modelled with BiLSTMs, fused with bidirectional '
            'cross-attention and classified into six classes with a KL-divergence objective.</desc>\n'
            '<defs>\n')
markers = []
for mid, col in [("a-ink", INK), ("a-eeg", EEG), ("a-spec", SPEC), ("a-fus", FUS), ("a-cls", CLS), ("a-muted", MUTED)]:
    markers.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                   f'orient="auto-start-reverse"><path d="M0,0.5 L10,5 L0,9.5 z" fill="{col}"/></marker>')
svg = (svg_head + "\n".join(markers) + "\n</defs>\n"
       f'<rect width="{W}" height="{H:.0f}" fill="#FFFFFF"/>\n' + "\n".join(out) + "\n</svg>\n")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT} ({W}x{H:.0f}, {len(svg) / 1024:.0f} KB)")
