#!/usr/bin/env python3
"""Draw the 24 November 2026 front page into assets/entry.png.

A one-page newspaper rendered with Pillow and the system DejaVu fonts:
a navy masthead naming the day, a lead panel on Nvidia reinstating
Jensen Huang, six story cards in a 3x2 grid (each with a small drawn
motif of its own), and a dark footer ticker of shorter items. Every
story comes from news first reported on Tuesday 24 November 2026,
gathered from live sources while building this entry (Reuters, AP,
BBC, The Guardian, India Today). The output is a 1024x1024 PNG under
1 MiB, byte-identical on every run.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
EDGE = 28
PAPER = (252, 251, 245)
INK = (22, 22, 22)
NAVY = (13, 48, 66)
NAVY_DARK = (8, 34, 48)
GOLD = (196, 154, 36)
RED = (171, 32, 32)
GREY = (112, 112, 104)
LINE = (208, 208, 198)
CARD_BG = (248, 248, 240)
TEAL = (46, 120, 138)
ORANGE = (214, 96, 32)

FONTS = Path("/usr/share/fonts/truetype/dejavu")


def load(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def serif_b(size):
    return load("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return load("DejaVuSerif.ttf", size)


def sans_b(size):
    return load("DejaVuSans-Bold.ttf", size)


def sans(size):
    return load("DejaVuSans.ttf", size)


def wrapped(draw, text, fnt, width):
    """Greedy word wrap: a list of lines that fit inside width."""
    out = []
    for block in text.split("\n"):
        line = ""
        for word in block.split():
            trial = (line + " " + word).strip()
            if not line or draw.textlength(trial, font=fnt) <= width:
                line = trial
            else:
                out.append(line)
                line = word
        if line:
            out.append(line)
    return out


def flow(draw, text, fnt, width, x, y, fill=INK, gap=4):
    """Draw wrapped text starting at (x, y); return the y below it."""
    for line in wrapped(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def cracked_globe(draw, cx, cy, r):
    """A globe disc with meridians, parallels and a white crack."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL,
                 outline=NAVY_DARK, width=4)
    for k in (1, 2, 3):
        rx = r * k / 4
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r],
                     outline=(255, 255, 255), width=2)
    for frac in (-0.5, 0.0, 0.5):
        yy = cy + frac * r
        half = int(r * math.sqrt(max(0.0, 1 - frac * frac)))
        draw.line([cx - half, yy, cx + half, yy],
                  fill=(255, 255, 255), width=2)
    crack = [(cx - r * 0.15, cy - r * 0.9), (cx + r * 0.1, cy - r * 0.45),
             (cx - r * 0.2, cy - r * 0.1), (cx + r * 0.25, cy + r * 0.25),
             (cx - r * 0.05, cy + r * 0.6), (cx + r * 0.2, cy + r * 0.95)]
    draw.line(crack, fill=(255, 255, 255), width=5, joint="curve")


def ship_on_waves(draw, x, y, w, h):
    """A small ship riding three wave lines."""
    draw.polygon([(x + 6, y + 26), (x + w - 6, y + 26),
                  (x + w - 16, y + 42), (x + 16, y + 42)], fill=NAVY)
    draw.rectangle([x + w // 2 - 4, y + 6, x + w // 2 + 4, y + 26],
                   fill=NAVY_DARK)
    for yy in (y + 50, y + 60, y + 70):
        draw.arc([x, yy - 8, x + w, yy + 8], 200, 340, fill=TEAL, width=3)


def radar(draw, x, y, w, h):
    """A radar screen: concentric arcs, a sweep line and one blip."""
    cx, cy = x + w // 2, y + h // 2
    for r in (34, 24, 14):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 0, 360,
                 fill=TEAL, width=3)
    draw.line([cx, cy, cx + 26, cy - 26], fill=RED, width=3)
    draw.ellipse([cx + 20, cy - 32, cx + 30, cy - 22], fill=RED)


def flame(draw, x, y, w, h):
    """A flame: an outer teardrop with a gold inner tongue."""
    cx = x + w // 2
    draw.polygon([(cx, y + 2), (cx + w * 0.32, y + h * 0.45),
                  (cx + w * 0.22, y + h * 0.75), (cx, y + h),
                  (cx - w * 0.22, y + h * 0.75),
                  (cx - w * 0.32, y + h * 0.45)], fill=ORANGE)
    draw.polygon([(cx, y + h * 0.35), (cx + w * 0.16, y + h * 0.62),
                  (cx, y + h * 0.85), (cx - w * 0.16, y + h * 0.62)],
                 fill=GOLD)


def anchor(draw, x, y, w, h):
    """A ship's anchor: ring, shank, crossbar and two flukes."""
    cx = x + w // 2
    draw.ellipse([cx - 8, y + 4, cx + 8, y + 20], outline=NAVY, width=4)
    draw.line([cx, y + 20, cx, y + h - 14], fill=NAVY, width=5)
    draw.line([cx - 18, y + 28, cx + 18, y + 28], fill=NAVY, width=5)
    draw.arc([cx - 26, y + h - 40, cx + 26, y + h + 4], 0, 180,
             fill=NAVY, width=5)
    draw.polygon([(cx - 26, y + h - 18), (cx - 12, y + h - 18),
                  (cx - 22, y + h - 4)], fill=NAVY)
    draw.polygon([(cx + 26, y + h - 18), (cx + 12, y + h - 18),
                  (cx + 22, y + h - 4)], fill=NAVY)


def chip(draw, x, y, w, h):
    """A processor chip: a dark square, a gold core and pins on all sides."""
    cx, cy = x + w // 2, y + h // 2
    s = 24
    for i in range(4):
        off = -18 + i * 12
        draw.line([cx + off, cy - s - 10, cx + off, cy - s],
                  fill=GOLD, width=3)
        draw.line([cx + off, cy + s, cx + off, cy + s + 10],
                  fill=GOLD, width=3)
        draw.line([cx - s - 10, cy + off, cx - s, cy + off],
                  fill=GOLD, width=3)
        draw.line([cx + s, cy + off, cx + s + 10, cy + off],
                  fill=GOLD, width=3)
    draw.rectangle([cx - s, cy - s, cx + s, cy + s], fill=NAVY_DARK,
                   outline=GOLD, width=3)
    draw.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=GOLD)


def football(draw, x, y, w, h):
    """A football beside a chequered flag strip."""
    cx, cy, r = x + 26, y + h // 2, 24
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
                 outline=INK, width=3)
    draw.polygon([(cx, cy - 9), (cx + 9, cy - 3), (cx + 5, cy + 8),
                  (cx - 5, cy + 8), (cx - 9, cy - 3)], fill=INK)
    for k in range(4):
        sq = 8
        xx = x + 52 + (k % 2) * sq
        yy = y + 18 + (k // 2) * sq
        if (k % 2 == 0) != ((k // 2) % 2 == 0):
            draw.rectangle([xx, yy, xx + sq, yy + sq], fill=INK)


MOTIFS = {"globe": cracked_globe, "waves": ship_on_waves,
          "radar": radar, "flame": flame, "anchor": anchor,
          "chip": chip, "ball": football}


def card(draw, x, y, w, h, motif, kicker, head, body):
    draw.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE,
                   width=2)
    draw.rectangle([x, y, x + w, y + 4], fill=NAVY)
    if motif == "globe":
        cracked_globe(draw, x + 42, y + 42, 28)
    else:
        MOTIFS[motif](draw, x + 12, y + 12, 64, 64)
    tx = x + 88
    draw.text((tx, y + 14), kicker, font=sans_b(16), fill=RED)
    end = flow(draw, head, serif_b(24), w - 102, tx, y + 38, gap=2)
    flow(draw, body, serif(17), w - 28, x + 14, end + 6, gap=3)


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    d.rectangle([0, 0, SIZE, 148], fill=NAVY)
    chip(d, 34, 42, 104, 104)
    d.text((158, 26), "THE WORLD IN ONE PAGE", font=serif_b(52),
           fill=(255, 255, 255))
    d.text((160, 92), "TUESDAY  ·  24 NOVEMBER 2026", font=sans_b(30),
           fill=GOLD)
    d.text((158, 124), "make.fun daily news picture",
           font=sans(17), fill=(200, 220, 224))
    d.rectangle([0, 148, SIZE, 154], fill=GOLD)

    # Lead story: Nvidia reinstates Jensen Huang.
    ly = 168
    d.rectangle([EDGE, ly, SIZE - EDGE, ly + 236], fill=CARD_BG,
                outline=LINE, width=2)
    chip(d, 52, ly + 66, 184, 104)
    d.rectangle([52, ly + 196, 230, ly + 224], fill=RED)
    d.text((60, ly + 200), "BACK IN CHARGE", font=sans_b(18),
           fill=(255, 255, 255))
    tx = 330
    d.text((tx, ly + 16), "TECH  ·  NVIDIA", font=sans_b(18), fill=RED)
    end = flow(d, "Nvidia brings back Huang\nas chief executive",
               serif_b(40), SIZE - EDGE - tx - 16, tx, ly + 46, gap=2)
    flow(d, "The board unanimously reinstates Jensen Huang as CEO days "
            "after his resignation; Trump says \u201cI made the deal\u201d "
            "and insists Huang poses no national security threat.",
         serif(21), SIZE - EDGE - tx - 16, tx, end + 8, gap=4)

    # Six story cards, 3 x 2.
    stories = [
        ("waves", "LIBYA",
         "Ukraine sinks Russian ship off Libya",
         "Kyiv says sea drones sank a Russian corvette at Benghazi; "
         "Libya\u2019s UN-backed government condemns the strike."),
        ("radar", "POLAND",
         "NATO sends jets after missiles land",
         "Three Russian missiles fell on Poland on Friday; NATO "
         "deploys early-warning aircraft to its eastern flank."),
        ("globe", "CLIMATE",
         "COP31 fallout: blame and despair",
         "Australia faces calls for resignations after the talks "
         "collapse; Pacific nations voice despair at the failure."),
        ("flame", "INDONESIA",
         "Factory fire rescue goes on",
         "Rescue teams keep searching for dozens missing after the "
         "blaze at an Indonesian factory."),
        ("anchor", "IRAN",
         "Iran vows to defy US naval blockade",
         "Tehran says it will use \u201call its tools\u201d against the "
         "American blockade as tensions rise."),
        ("ball", "SPORT",
         "Seven-goal thriller stuns Inter",
         "Tresoldi\u2019s hat-trick caps a wild night at San Siro as "
         "Inter fall to a historic home defeat."),
    ]
    cw = (SIZE - 2 * EDGE - 2 * 16) // 3
    ch = 216
    top = 424
    for i, (motif, kicker, head, body) in enumerate(stories):
        cx = EDGE + (i % 3) * (cw + 16)
        cy = top + (i // 3) * (ch + 16)
        card(d, cx, cy, cw, ch, motif, kicker, head, body)

    # Footer ticker.
    fy = 888
    d.rectangle([0, fy, SIZE, SIZE], fill=NAVY_DARK)
    ticker = ("KOREA  ·  Evacuation alert on Ulleung after a Russian jet "
              "enters its airspace    —    GAZA  ·  Israeli strikes kill "
              "three, including a UN aid worker    —    INDIA–NEPAL  ·  "
              "Delhi pledges $1.6bn in flood relief    —    EUROPE  ·  "
              "Search begins for a new ECB chief as Lagarde resigns    —    "
              "HEALTH  ·  Kenya discharges its last Ebola patient as the "
              "DRC toll passes 5,300")
    flow(d, ticker, sans(19), SIZE - 2 * EDGE, EDGE, fy + 16,
         fill=(235, 238, 235), gap=8)

    out = Path(__file__).resolve().parent / "assets" / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
