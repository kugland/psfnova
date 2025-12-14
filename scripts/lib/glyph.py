import re
from PIL import Image
from functools import cached_property
from pathlib import Path
from functools import cache
from .codepoint import Codepoint
from .types import Bitmap, BitmapRow, GlyphSize, ZeroOrOne

GLYPHS_DIR = Path(__file__).parent / ".." / ".." / "glyphs"


class Glyph:
    name: str
    size: GlyphSize
    codepoint: Codepoint

    def __init__(self, file: Path) -> None:
        self.name = file.stem
        parent_dir = file.parent.name
        if parent_dir in ["1x", "2x"]:
            self.size = parent_dir  # type: ignore
        else:
            raise ValueError(f"Invalid glyph size directory: {parent_dir}")
        if m := re.match(r"^([0-9A-Fa-f]{4,6}) .*$", self.name):
            self.codepoint = Codepoint.from_string(f"U+{m.group(1)}")
        else:
            raise ValueError(f"Invalid glyph name: {file}")

    @cached_property
    def bitmap(self) -> Bitmap:
        img_path = GLYPHS_DIR / self.size / f"{self.name}.png"
        img = Image.open(img_path).convert("L")
        width, height = img.size
        bitmap: Bitmap = []
        for y in range(height):
            row: BitmapRow = []
            for x in range(width):
                pixel: ZeroOrOne = 1 if img.getpixel((x, y)) == 0 else 0  # type: ignore
                row.append(pixel)
            bitmap.append(row)
        return bitmap

    def __repr__(self) -> str:
        return (
            f"Glyph(codepoint={self.codepoint} name='{self.name}', size='{self.size}')"
        )

    @staticmethod
    @cache
    def list_by_size(size: GlyphSize) -> list["Glyph"]:
        parent_dir = GLYPHS_DIR / size
        return [
            Glyph(file)
            for file in parent_dir.iterdir()
            if file.is_file() and file.suffix == ".png"
        ]

    @staticmethod
    @cache
    def list_all() -> list["Glyph"]:
        return Glyph.list_by_size("1x") + Glyph.list_by_size("2x")

    @staticmethod
    @cache
    def map_by_size(size: GlyphSize) -> dict[int, "Glyph"]:
        result: dict[int, Glyph] = {}
        for glyph in Glyph.list_by_size(size):
            result[glyph.codepoint.value] = glyph
        return result

    @staticmethod
    @cache
    def map_all() -> dict[GlyphSize, dict[int, "Glyph"]]:
        return {
            "1x": Glyph.map_by_size("1x"),
            "2x": Glyph.map_by_size("2x"),
        }
