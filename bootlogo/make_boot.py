r"""Quantix boot screen for the G301 (720x1560): a still logo (for logo.bin after the mtkclient backup) and an
Android bootanimation.zip (installed with a Magisk module after root). Everything is drawn in code.

    F:\Quantix_Master_Vault\simba_desktop_companion\.venv\Scripts\python.exe make_boot.py

Output: quantix_logo.png, bootanimation.zip, preview.png
"""
from __future__ import annotations

import io
import math
import random
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r"F:\Quantix_Master_Vault\simba_desktop_companion")
import simba_drawn  # noqa: E402

W, H, FPS = 720, 1560, 30
BG, TEAL, ORANGE, WHITE = (6, 9, 20), (45, 212, 191), (224, 123, 57), (236, 254, 255)
CY = 760                                                     # blade line


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def backdrop() -> Image.Image:
    rng = random.Random(7)
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for _ in range(260):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.choice([0.6, 0.8, 1.0, 1.4])
        a = rng.randint(60, 200)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(a, a, min(255, a + 30)))
    for i in range(9):                                       # faint data grid rising from the bottom
        y = H - 40 - i * i * 6
        d.line([(0, y), (W, y)], fill=(12, 40, 48), width=1)
    for k in range(-6, 7):
        d.line([(W / 2 + k * 18, H - 40 - 64 * 6), (W / 2 + k * 120, H)], fill=(12, 40, 48), width=1)
    return im


SIMBA = simba_drawn.FRAMES["idle"]()
SIMBA = SIMBA.crop(SIMBA.getbbox())
SIMBA = SIMBA.resize((int(SIMBA.width * 300 / SIMBA.height), 300), Image.LANCZOS)


def frame(base: Image.Image, blade: float, text: float, cat: float, pulse: float = 1.0) -> Image.Image:
    """blade, text, cat: 0..1 progress; pulse scales the glow."""
    im = base.copy().convert("RGBA")
    half = 290 * blade
    if blade > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(glow)
        g.line([(W / 2 - half, CY), (W / 2 + half, CY)], fill=TEAL + (int(200 * pulse),), width=34)
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16)))
        d = ImageDraw.Draw(im)
        d.line([(W / 2 - half, CY), (W / 2 + half, CY)], fill=WHITE + (255,), width=7)
        d.rounded_rectangle((W / 2 - 44, CY - 9, W / 2 + 44, CY + 9), 4, fill=(148, 163, 184, 255), outline=(30, 41, 59, 255), width=2)
    if cat > 0:
        c = SIMBA.copy()
        c.putalpha(c.getchannel("A").point(lambda v: int(v * cat)))
        im.alpha_composite(c, (int(W / 2 - c.width / 2), int(CY - 40 - c.height)))
    if text > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.text((W / 2, CY + 95), "QUANTIX", font=font(108), anchor="mm", fill=WHITE + (int(255 * text),))
        d.text((W / 2, CY + 170), "COMMAND CENTER", font=font(34), anchor="mm", fill=ORANGE + (int(235 * text),))
        glow = layer.filter(ImageFilter.GaussianBlur(10))
        im.alpha_composite(glow)
        im.alpha_composite(layer)
    return im.convert("RGB")


def png(img: Image.Image) -> bytes:
    b = io.BytesIO()
    img.save(b, "PNG", optimize=True)
    return b.getvalue()


def main() -> None:
    base = backdrop()
    ease = lambda t: 1 - (1 - min(1, max(0, t))) ** 3
    part0 = [frame(base, ease(i / 14), ease((i - 14) / 14), ease((i - 26) / 14)) for i in range(45)]
    part1 = [frame(base, 1, 1, 1, 0.75 + 0.25 * math.sin(2 * math.pi * i / 30)) for i in range(30)]
    part1[0].save(HERE / "quantix_logo.png")
    with zipfile.ZipFile(HERE / "bootanimation.zip", "w", zipfile.ZIP_STORED) as z:   # Android needs stored, not deflated
        z.writestr("desc.txt", f"{W} {H} {FPS}\np 1 0 part0\np 0 0 part1\n")
        for name, frames in (("part0", part0), ("part1", part1)):
            for i, f in enumerate(frames):
                z.writestr(f"{name}/{i:03d}.png", png(f))
    strip = Image.new("RGB", (6 * 240, 520))
    for k, f in enumerate([part0[6], part0[14], part0[22], part0[30], part0[44], part1[15]]):
        strip.paste(f.resize((240, 520)), (k * 240, 0))
    strip.save(HERE / "preview.png")
    print((HERE / "bootanimation.zip").stat().st_size >> 10, "KB")


if __name__ == "__main__":
    main()
