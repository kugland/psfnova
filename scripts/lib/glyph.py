import re
from PIL import Image
from functools import cached_property
from pathlib import Path
from typing import Literal
from typing import Generator

from lib.codepoint import Codepoint

GLYPHS_DIR = Path(__file__).parent / ".." / ".." / "glyphs"

class Glyph:
    _name: str
    _size: Literal['1x'] | Literal['2x']
    _codepoint: Codepoint

    def __init__(self, file: str) -> None:
        self._name = Path(file).stem
        parent_dir = Path(file).parent.name
        if parent_dir in ['1x', '2x']:
            self._size = parent_dir  # type: ignore
        else:
            raise ValueError(f"Invalid glyph size directory: {parent_dir}")
        if m := re.match(r'^([0-9A-Fa-f]{4,6}) .*$', self._name):
            self._codepoint = Codepoint.from_string(f'U+{m.group(1)}')
        else:
            raise ValueError(f"Invalid glyph name: {file}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> Literal['1x'] | Literal['2x']:
        return self._size

    @property
    def codepoint(self) -> Codepoint:
        return self._codepoint

    @cached_property
    def bitmap(self) -> list[list[Literal[0] | Literal[1]]]:
        img_path = GLYPHS_DIR / self._size / f"{self._name}.png"
        img = Image.open(img_path)
        img = img.convert('L')
        width, height = img.size
        bitmap = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = 1 if img.getpixel((x, y)) == 0 else 0
                row.append(pixel)
            bitmap.append(row)
        return bitmap


    def __repr__(self) -> str:
        return f"Glyph(codepoint={self._codepoint} name='{self._name}', size='{self._size}')"

    @staticmethod
    def list_by_size(size: Literal['1x'] | Literal['2x']) -> Generator['Glyph', None, None]:
        parent_dir = GLYPHS_DIR / size
        for file in parent_dir.iterdir():
            if file.is_file() and file.suffix == '.png':
                yield Glyph(str(file))

    @staticmethod
    def list_all() -> Generator['Glyph', None, None]:
        for size in ['1x', '2x']:
            yield from Glyph.list_by_size(size)
