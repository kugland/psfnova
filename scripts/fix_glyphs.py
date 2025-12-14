from PIL import Image
from pathlib import Path
import re
import unicodedata


def get_new_path(glyph_path: Path) -> Path:
    """Extract the Unicode codepoint and name from the filename"""
    if match := re.match(
        r"(?P<cp>[0-9A-Fa-f]{4}) - (?P<old>.*)[.]\w{3,4}", glyph_path.name
    ):
        cp = int(match.group("cp"), 16)
        old = match.group("old")
        try:
            name = unicodedata.name(chr(cp)).lower()
        except ValueError:
            name = old.lower()
        dirname = glyph_path.parent
        return dirname / Path(f"{cp:04X} - {name}.png")
    else:
        raise ValueError(f"Filename {glyph_path.name} does not match expected format")


def process_one_glyph(glyph_path: Path):
    # First create a new image to discard any metadata
    image = Image.open(glyph_path)
    data = list(image.get_flattened_data())  # type: ignore
    image = Image.new(image.mode, image.size)
    image.putdata(data)  # type: ignore

    # Then add a white background if image is RGBA
    if image.mode == "RGBA":
        size = (image.width, image.height)
        white = (255, 255, 255, 255)
        background = Image.new("RGBA", size, white)
        image = Image.alpha_composite(background, image)

    # Then, if mode is not black and white, rewrite it as black and white
    if image.mode != "1":
        image = image.convert("L")
        image = image.point(lambda x: 0 if x < 128 else 255, "1")  # type: ignore

    new_path = get_new_path(glyph_path)
    image.save(new_path)
    if new_path != glyph_path:
        glyph_path.unlink()


def process_all_glyphs():
    GLYPHS_DIR = Path(__file__).parent.parent / "glyphs"
    for size in ["1x", "2x"]:
        parent_dir = GLYPHS_DIR / size
        glyph_files = parent_dir.glob("[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f] *")
        for glyph_file in glyph_files:
            process_one_glyph(parent_dir / glyph_file)


def main():
    process_all_glyphs()


if __name__ == "__main__":
    main()
