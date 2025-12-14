from .lib import Charset, Font, Psfu
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Build the PSF Nova font from glyphs")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="psfnova.psfu",
        help="Path to the output PSF font file (default: psfnova.psfu)",
    )
    parser.add_argument(
        "--size",
        "-s",
        type=str,
        choices=["1x", "2x"],
        default="1x",
        help="Glyph size to use for the font (default: 1x)",
    )
    parser.add_argument(
        "--base-charset",
        "-b",
        type=str,
        choices=sorted([c.name for c in Charset.list_all()]),
        default="ascii",
        help="Base charset to include in the font (default: ascii)",
    )
    parser.add_argument(
        "--additional-charsets",
        "-a",
        type=str,
        nargs="*",
        choices=sorted([c.name for c in Charset.list_all()]),
        help="Additional charsets to include in the font (default: none)",
        action="append",
    )
    parser.add_argument(
        "--extra-glyphs",
        "-g",
        type=str,
        nargs="*",
        help="Additional glyph codepoints to include in the font (default: none)",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print(f"Building PSF Nova @{args.size}")
    print("Included charsets:")
    print(f" - {args.base_charset} (base)")
    if args.additional_charsets:
        for charset in args.additional_charsets:
            print(f" - {charset[0]}")

    if args.extra_glyphs:
        print("Included extra glyphs:")
        for codepoint in args.extra_glyphs:
            codepoint = int(codepoint, 16)
            print(f" - U+{codepoint:04X}")

    font = Font(args.size)
    font.add_codepoint(0, 0)  # The PSF spec requires the first slot to be empty.
    font.add_charset(Charset("ascii"), use_charset_slots=True)
    font.add_charset(Charset(args.base_charset), use_charset_slots=True)
    if args.additional_charsets:
        for charset_name in args.additional_charsets:
            font.add_charset(Charset(charset_name[0]), use_charset_slots=False)

    if args.extra_glyphs:
        for codepoint in args.extra_glyphs:
            font.add_codepoint(int(codepoint, 16), None)

    psfu = Psfu(font)
    psfu.write(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
