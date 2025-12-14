import struct
from pathlib import Path
from .font import Font
from .types import Bitmap, BitmapRow


class Psfu:
    """Serializes a Font instance into the PSF2 binary format."""

    PSF2_MAGIC = bytes([0x72, 0xB5, 0x4A, 0x86])
    PSF2_MAXVERSION = 0
    PSF2_HAS_UNICODE_TABLE = 0x01
    PSF2_SEPARATOR = 0xFF
    PSF2_HEADER_SIZE = 32

    _font: Font
    _height: int
    _width: int
    _charsize: int
    _length: int

    def __init__(self, font: Font) -> None:
        if not font.slots:
            raise ValueError("Font has no glyphs")
        self._font = font
        self._height = 32 if font.size == "2x" else 16
        self._width = 16 if font.size == "2x" else 8
        self._charsize = 64 if font.size == "2x" else 16
        # The Linux kernel (fbcon) only accepts fonts with exactly 256 or 512
        # glyphs, so round up to the nearest accepted value.
        max_slot = max(font.slots.keys())
        self._length = 256 if max_slot < 256 else 512

    def _pack_row(self, row: BitmapRow) -> bytes:
        """Pack a single bitmap row into bytes (MSB-first, zero-padded)."""
        byte_width = (self._width + 7) // 8
        result = bytearray(byte_width)
        for i, bit in enumerate(row):
            if bit:
                result[i // 8] |= 0x80 >> (i % 8)
        return bytes(result)

    def _pack_bitmap(self, bitmap: Bitmap) -> bytes:
        """Pack a full glyph bitmap into bytes."""
        return b"".join(self._pack_row(row) for row in bitmap)

    def _build_header(self, flags: int) -> bytes:
        """Build the 32-byte PSF2 header."""
        return (
            self.PSF2_MAGIC
            + struct.pack(
                "<6I",
                self.PSF2_MAXVERSION,  # version
                self.PSF2_HEADER_SIZE,  # headersize
                flags,  # flags
                self._length,  # length (number of glyphs)
                self._charsize,  # charsize (bytes per glyph)
                self._height,  # height
            )
            + struct.pack("<I", self._width)
        )  # width

    def _build_glyph_data(self) -> bytes:
        """Build the glyph bitmap section, filling gaps with blank glyphs."""
        blank = bytes(self._charsize)
        parts: list[bytes] = []
        for slot in range(self._length):
            bitmap = self._font.slots.get(slot)
            parts.append(self._pack_bitmap(bitmap) if bitmap is not None else blank)
        return b"".join(parts)

    def _build_unicode_table(self) -> bytes:
        """Build the Unicode mapping table (UTF-8 encoded codepoints per slot)."""
        parts: list[bytes] = []
        for slot in range(self._length):
            codepoints = self._font.unicode_map.get(slot)
            if codepoints:
                for cp in sorted(codepoints):
                    parts.append(chr(cp).encode("utf-8"))
            parts.append(bytes([self.PSF2_SEPARATOR]))
        return b"".join(parts)

    def generate(self) -> bytes:
        """Generate the complete PSF2 binary."""
        flags = self.PSF2_HAS_UNICODE_TABLE
        header = self._build_header(flags)
        glyphs = self._build_glyph_data()
        unicode_table = self._build_unicode_table()
        return header + glyphs + unicode_table

    def write(self, path: Path | str) -> None:
        """Write the PSF2 binary to a file."""
        data = self.generate()
        Path(path).write_bytes(data)
