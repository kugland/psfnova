from typing import Literal

GlyphSize = Literal["1x"] | Literal["2x"]
ZeroOrOne = Literal[0] | Literal[1]
Bitmap = list[list[ZeroOrOne]]
BitmapRow = list[ZeroOrOne]
