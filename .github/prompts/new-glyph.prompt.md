---
agent: agent
---

# New Glyph Creation

You'll be creating a new glyph for PSF Nova.

## Prerequisites

1. You will NOT create glyphs that already exist in the font.

2. You will ONLY create glyphs that can be composed using the existing glyphs in the font. For
   example, if I ask you to create a new glyph for "A with acute", you can create it by combining
   the existing "A" glyph with the existing "acute accent" glyph.

## Procedure

1. First the most appropriate glyphs in the font that can be combined to create the new glyph.

2. You'll look at the ASCII dump of the glyphs by running the following command:

```bash
pngtopam glyphs/[1x/2x]/[glyph-name].png | pnmtopnm -plain
```

3. You'll determine the name of the new glyph by running the following script:

```python
import unicodedata
codepoint = 0xE000  # Replace with the Unicode code point of the new glyph
print(f'{codepoint:04X} - {unicodedata.name(chr(codepoint)).lower()}.png')
```

4. When combining glyphs with diacritical marks, take care with the vertical positioning:
   - Diacritical marks on small letters are normally positioned lower than on capital letters
   - Diacritical marks on capital letters are typically positioned higher
   - Exception: For small letters with ascenders (like d, h, k, l, t), diacritical marks may need to be positioned higher to avoid collision with the ascender

5. You'll analyze the ASCII dump and compose a new ASCII representation of the new glyph by
   combining the existing glyphs. This you'll write as a PBM file to `/tmp/[some-name].pbm`.

6. You'll convert the new ASCII representation back into a PNG image using the following command:

```bash
pnmtoimage -plain '/tmp/[some-name].pbm' > glyphs/[1x/2x]/[new-glyph-name].png
```
