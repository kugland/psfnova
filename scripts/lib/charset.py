import re
import os
from pathlib import Path
from typing import Generator
from .codepoint import Codepoint

CHARSETS_DIR = Path(__file__).parent / ".." / ".." / "charsets"

class Charset:
    _name: str
    _codepoints: list[tuple[int | None, Codepoint]]

    def __init__(self, name: str) -> None:
        self._name = name
        self._codepoints = [*self._load_codepoints(CHARSETS_DIR / f"{name}.txt")]

    @property
    def name(self) -> str:
        return self._name

    def codepoints(self) -> Generator[Codepoint, None, None]:
        for _, cp in self._codepoints:
            yield cp

    def map(self) -> Generator[tuple[int | None, Codepoint], None, None]:
        for cp in self._codepoints:
            yield cp

    def __repr__(self) -> str:
        return f"Charset(name='{self._name}', codepoints={len(self._codepoints)})"

    def _load_codepoints(self, charset_file: str) -> Generator[tuple[int | None, Codepoint], None, None]:
        with open(charset_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = re.sub(r'#.*$', '', line)
                line = re.sub(r'\s+', ' ', line)
                line = re.sub(r'^ ', '', line)
                line = re.sub(r' $', '', line)
                if not line:
                    continue
                elif m := re.match(r'^([0-9A-Fa-f]{2}|XX) (U\+[0-9A-Fa-f]{4,6})$', line):
                    index = None if m.group(1) == 'XX' else int(m.group(1), 16)
                    codepoint = Codepoint.from_string(m.group(2))
                    yield (index, codepoint)
                    continue
                else:
                    raise ValueError(f"Invalid line in charset file '{charset_file}': {line}")

    @staticmethod
    def list_all():
        return [Charset(f[:-4]) for f in os.listdir(CHARSETS_DIR) if f.endswith('.txt')]
