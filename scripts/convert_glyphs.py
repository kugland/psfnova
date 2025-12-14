from PIL import Image
from pathlib import Path

def process_one_glyph(glyph_path: Path):
    # First create a new image to discard any metadata
    image = Image.open(glyph_path)
    data = list(image.getdata())
    image = Image.new(image.mode, image.size)
    image.putdata(data)

    # Then add a white background if image is RGBA
    if image.mode == "RGBA":
        size = (image.width, image.height)
        white = (255, 255, 255, 255)
        background = Image.new("RGBA", size, white)
        image = Image.alpha_composite(background, image)

    # Then, if mode is not black and white, rewrite it as black and white
    if image.mode != "1":
        image = image.convert("L")
        image = image.point(lambda x: 0 if x < 128 else 255, "1")

    image.save(glyph_path)

GLYPHS_DIR = Path(__file__).parent.parent / "glyphs"

if __name__ == "__main__":
    for size in ['1x', '2x']:
        parent_dir = GLYPHS_DIR / size
        for glyph_file in parent_dir.glob("[0-9A-F][0-9A-F][0-9A-F][0-9A-F] *.png"):
            process_one_glyph(parent_dir / glyph_file)
