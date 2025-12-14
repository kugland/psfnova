#!/usr/bin/env python3

from unicodedata import name as unicode_name
from scripts.lib import Charset
from scripts.lib import Glyph


def main() -> None:
    for charset in Charset.list_all():
        codepoints = set((c.value for c in charset.codepoints()))
        for size in ["1x", "2x"]:
            available: set[int] = set()
            for glyph in Glyph.list_by_size(size):
                available.add(glyph.codepoint.value)
            missing = codepoints.difference(available)
            if missing:
                name = charset.name
                print(
                    f"Charset '{name}' is missing {len(missing)} glyphs of size '{size}':"
                )
                for cp in sorted(missing):
                    print(f"    - U+{cp:04X}    {unicode_name(chr(cp), '<no name>')}")


if __name__ == "__main__":
    main()
