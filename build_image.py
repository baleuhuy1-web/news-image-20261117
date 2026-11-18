"""Compose the entry image: a one-page newspaper front page for
Tuesday 17 November 2026.

Six AI-drawn panels live in ``assets/``; every word on the page is set
here with PIL so the lettering is exact and never garbled.  The result
is written to ``entry.png`` beside this file (1024x1024, under 1 MiB).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FONTS = Path("/usr/share/fonts/truetype/dejavu")

W = H = 1024
PAPER = (247, 242, 231)
INK = (18, 18, 18)
GREY = (70, 66, 60)
CRIMSON = (158, 27, 42)
WHITE = (255, 255, 255)

MARGIN = 28
CONTENT_W = W - 2 * MARGIN
GUTTER = 20
COL_W = (CONTENT_W - GUTTER) // 2
IMG_H = 128
HEAD_SIZE = 26
SUB_SIZE = 18

STORIES = [
    ("panel1.png", "CRIMEAN BRIDGE SPAN COLLAPSES",
     "Ukraine's strike drops a road section into the Kerch Strait"),
    ("panel2.png", "TRUMP OPENS ASIA TRIP IN MANILA",
     "Quad leaders meet for the first time since his return"),
    ("panel3.png", "IRANIAN DRONES TARGET US BASE IN BAHRAIN",
     "Defences intercept as tanker fires spread in Hormuz"),
    ("panel4.png", "WEST URGES GAZA CROSSINGS OPEN",
     "UN report: 1.7 million displaced face the winter"),
    ("panel5.png", "US LOSES MEASLES-FREE STATUS",
     "Worst case count in 30 years ends the designation"),
    ("panel6.png", "JAPAN SCRAMBLES JETS",
     "Russian aircraft violate airspace as Tokyo protests"),
]

FOOTER_LINES = [
    "BRITAIN SANCTIONS SETTLEMENT FIRMS • FIVE EU STATES REVIVE RWANDA PLAN",
    "DEPARDIEU ADMITS ASSAULT CHARGES",
]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def fit_font(name: str, text: str, size: int, max_w: int) -> ImageFont.FreeTypeFont:
    """Shrink the font until the single line fits max_w."""
    f = font(name, size)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    while size > 10 and probe.textlength(text, font=f) > max_w:
        size -= 2
        f = font(name, size)
    return f


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def cover(path: Path, w: int, h: int) -> Image.Image:
    """Resize and centre-crop an image so it exactly fills w x h."""
    im = Image.open(path).convert("RGB")
    scale = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)),
                   Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def main() -> None:
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # Masthead with rules above and below.
    d.rectangle([MARGIN, 16, W - MARGIN, 20], fill=INK)
    d.rectangle([MARGIN, 25, W - MARGIN, 27], fill=INK)
    masthead = fit_font("DejaVuSerif-Bold.ttf", "THE WORLD TODAY", 96, CONTENT_W)
    d.text((W // 2, 88), "THE WORLD TODAY", font=masthead, fill=INK,
           anchor="mm")
    d.rectangle([MARGIN, 138, W - MARGIN, 140], fill=INK)

    # Crimson date band.
    d.rectangle([MARGIN, 148, W - MARGIN, 196], fill=CRIMSON)
    date_f = fit_font("DejaVuSans-Bold.ttf", "TUESDAY 17 NOVEMBER 2026", 34,
                      CONTENT_W - 40)
    d.text((W // 2, 172), "TUESDAY 17 NOVEMBER 2026", font=date_f,
           fill=WHITE, anchor="mm")
    d.rectangle([MARGIN, 204, W - MARGIN, 207], fill=INK)

    # Story grid: two columns, three rows.
    head_f = font("DejaVuSans-Bold.ttf", HEAD_SIZE)
    sub_f = font("DejaVuSans.ttf", SUB_SIZE)
    grid_top = 216
    row_h = (950 - grid_top) // 3
    for i, (img_name, headline, sub) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = MARGIN + col * (COL_W + GUTTER)
        y = grid_top + row * row_h
        page.paste(cover(ASSETS / img_name, COL_W, IMG_H), (x, y))
        d.rectangle([x, y, x + COL_W - 1, y + IMG_H - 1], outline=INK, width=2)
        cy = y + IMG_H + 7
        for line in wrap(d, headline, head_f, COL_W):
            d.text((x, cy), line, font=head_f, fill=INK)
            cy += 31
        for line in wrap(d, sub, sub_f, COL_W):
            d.text((x, cy + 1), line, font=sub_f, fill=GREY)
            cy += 22

    # Black footer band with the day's smaller headlines.
    d.rectangle([0, 950, W, H], fill=INK)
    foot_f = font("DejaVuSans-Bold.ttf", 20)
    fy = 964
    for line in FOOTER_LINES:
        f = fit_font("DejaVuSans-Bold.ttf", line, 20, CONTENT_W)
        d.text((W // 2, fy), line, font=f, fill=WHITE, anchor="ma")
        fy += 28

    out = ROOT / "entry.png"
    page.save(out, optimize=True)
    if out.stat().st_size > 1_048_576:  # keep the file under the 1 MiB cap
        page.quantize(colors=256, method=Image.MEDIANCUT).convert("RGB").save(
            out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
