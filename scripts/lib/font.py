from .glyph import Glyph
from .charset import Charset
from .types import Bitmap, GlyphSize
from collections import OrderedDict


class Font:
    size: GlyphSize
    slots: OrderedDict[int, Bitmap]
    unicode_map: dict[int, set[int]]
    _included_codepoints: set[int]

    def __init__(self, size: GlyphSize) -> None:
        self.size = size
        self.slots = OrderedDict()
        self.unicode_map = {}
        self._included_codepoints = set()

    def _find_slot_with_bitmap(self, bitmap: Bitmap) -> int | None:
        for slot, b in self.slots.items():
            if slot != 0 and b == bitmap:
                return slot
        return None

    def _first_available_slot(self) -> int | None:
        for slot in range(512):
            if slot not in self.slots:
                return slot
        return None

    def add_codepoint(self, codepoint: int, slot: int | None) -> None:
        if codepoint in self._included_codepoints:
            return

        if slot is not None and slot > 511:
            raise ValueError(f"Invalid slot number: {slot}")

        glyph_map = Glyph.map_by_size(self.size)  # Don’t worry, it’s cached.

        if (glyph := glyph_map.get(codepoint)) is None:
            raise ValueError(f"No glyph found: U+{codepoint:04X}@{self.size}")

        if slot:
            # If the slot is already occupied, check if it’s the same bitmap, fail if it’s not.
            if (bitmap := self.slots.get(slot)) is not None and bitmap != glyph.bitmap:
                raise ValueError(
                    f"Slot {slot} already occupied (trying to add U+{codepoint:04X})"
                )
        else:
            slot = self._find_slot_with_bitmap(glyph.bitmap)
            if slot is None:
                slot = self._first_available_slot()
                if slot is None:
                    raise ValueError(f"No available slots for U+{codepoint:04X}")

        self.slots[slot] = glyph.bitmap
        self._included_codepoints.add(codepoint)
        self.unicode_map.setdefault(slot, set()).add(codepoint)

    def add_charset(self, charset: Charset, use_charset_slots: bool = True) -> None:
        for slot, codepoint in charset.map():
            self.add_codepoint(codepoint.value, slot if use_charset_slots else None)
