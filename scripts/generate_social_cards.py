from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SIZE = (1200, 630)
PORTRAIT = ROOT / "profile.webp"
FONT_DIR = Path(r"C:\Windows\Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def make_card(path: str, accent: tuple[int, int, int], eyebrow: str, title: str, subtitle: str, footer: str) -> None:
    width, height = SIZE
    base = Image.new("RGB", SIZE)
    pixels = base.load()
    for y in range(height):
        t = y / (height - 1)
        color = (int(4 + 3 * t), int(8 + 5 * t), int(15 + 8 * t))
        for x in range(width):
            pixels[x, y] = color

    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((760, -180, 1360, 430), fill=(*accent, 64))
    glow_draw.ellipse((-260, 420, 500, 980), fill=(44, 111, 180, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(110))
    base = Image.alpha_composite(base.convert("RGBA"), glow)
    draw = ImageDraw.Draw(base)

    # A quiet technical grid keeps the card in the portfolio's visual language.
    grid = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for x in range(48, width, 48):
        grid_draw.line((x, 0, x, height), fill=(255, 255, 255, 9), width=1)
    for y in range(48, height, 48):
        grid_draw.line((0, y, width, y), fill=(255, 255, 255, 9), width=1)
    base = Image.alpha_composite(base, grid)
    draw = ImageDraw.Draw(base)

    draw.rounded_rectangle((78, 78, 87, 87), radius=4, fill=(*accent, 255))
    draw.text((105, 72), eyebrow.upper(), font=font("segoeuib.ttf", 17), fill=(*accent, 255), spacing=4)
    draw.text((76, 145), title, font=font("georgia.ttf", 70), fill=(247, 249, 252, 255))
    draw.line((82, 255, 565, 255), fill=(*accent, 185), width=2)
    draw.text((80, 288), subtitle, font=font("georgiai.ttf", 30), fill=(220, 228, 238, 255))
    draw.text((82, 530), footer.upper(), font=font("segoeuib.ttf", 15), fill=(155, 169, 187, 255), spacing=3)

    portrait = Image.open(PORTRAIT).convert("RGB")
    portrait = ImageOps.fit(portrait, (360, 360), method=Image.Resampling.LANCZOS, centering=(.5, .38))
    mask = Image.new("L", (360, 360), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 359, 359), fill=255)
    ring = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.ellipse((735, 120, 1121, 506), outline=(*accent, 210), width=2)
    ring_draw.ellipse((746, 131, 1110, 495), outline=(255, 255, 255, 40), width=1)
    base = Image.alpha_composite(base, ring)
    base.paste(portrait, (748, 133), mask)

    base.convert("RGB").save(ROOT / path, "JPEG", quality=90, optimize=True, progressive=True, subsampling=0)


make_card(
    "og-image.jpg",
    (121, 199, 255),
    "Portfolio · 2026",
    "Kaustuv Singh",
    "Creative Thinker · Problem Solver · Builder",
    "Useful Products  /  Thoughtful Design  /  Real-world Impact",
)
make_card(
    "og-image-client.jpg",
    (200, 255, 0),
    "Selected client projects",
    "Kaustuv Singh",
    "Useful ideas, shipped with care",
    "Commerce  /  Custom Software  /  Product Building",
)

print("Generated og-image.jpg and og-image-client.jpg (1200 x 630).")
