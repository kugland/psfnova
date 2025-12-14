{
  description = "PSF Nova is a terminal font specifically designed for use with the Linux VT";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    devshell.url = "github:numtide/devshell";
    flake-root.url = "github:srid/flake-root";
    flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1.tar.gz";
  };

  outputs = inputs @ {
    flake-parts,
    nixpkgs,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [
        inputs.devshell.flakeModule
        inputs.flake-root.flakeModule
      ];
      systems = nixpkgs.lib.systems.flakeExposed;

      perSystem = {
        pkgs,
        config,
        self',
        ...
      }: let
        inherit (pkgs) lib;
        python = pkgs.python314.withPackages (ps: with ps; [pillow types-pillow]);

        src = pkgs.lib.cleanSource ./.;

        mkArgs = opt: args: lib.escapeShellArgs (lib.flatten (map (c: [opt c]) args));

        mkFont = {
          size,
          suffix,
          base_charset,
          additional_charsets,
          additional_glyphs,
        }: let
          sizeSuffix =
            if size == "1x"
            then "8x16"
            else if size == "2x"
            then "16x32"
            else throw "Invalid size: ${size}";
          name = "psfnova-${suffix}-${sizeSuffix}";
          escapedName = lib.escapeShellArg "${name}.psfu";
        in
          pkgs.stdenvNoCC.mkDerivation {
            inherit name src;
            buildInputs = [python];
            buildPhase = ''
              mkdir -p "$out"
              ${python}/bin/python -m scripts.build_font \
                -b ${base_charset} \
                -s ${size} \
                ${mkArgs "-a" additional_charsets} \
                ${mkArgs "-g" additional_glyphs} \
                --out ${escapedName} \
                || (echo "Build failed with exit code $?"; exit 1)
            '';
            installPhase = ''
              mkdir -p "$out"
              mv ${escapedName} $out/${escapedName}
            '';
          };
        mkFontPair = {
          base_charset,
          suffix ? base_charset,
          additional_charsets ? [],
          additional_glyphs ? [],
        }: [
          (mkFont {
            inherit suffix base_charset additional_charsets additional_glyphs;
            size = "1x";
          })
          (mkFont {
            inherit suffix base_charset additional_charsets additional_glyphs;
            size = "2x";
          })
        ];
        flavors = (builtins.fromTOML (builtins.readFile ./flavors.toml)).flavor;
        allFonts = lib.flatten (map mkFontPair flavors);
      in {
        packages =
          builtins.listToAttrs (map (font: lib.nameValuePair font.name font) allFonts)
          // {
            psfnova = pkgs.symlinkJoin {
              name = "psfnova";
              paths = map (font: font.out) allFonts;
            };
            mkPsfnova = mkFont;
            default = self'.packages.psfnova;
          };
        devshells.default = {
          commands = [
            {
              name = "build-fonts";
              help = "Build the PSF Nova font (default command)";
              command = ''
                cd "$(${pkgs.lib.getExe config.flake-root.package})" &&
                mkdir -p fonts &&
                rm -f fonts/* &&
                cp ${self'.packages.psfnova}/* fonts/ &&
                chmod 644 fonts/*
              '';
            }
            {
              name = "missing-glyphs";
              help = "List missing glyphs in the font";
              command = ''
                cd "$(${pkgs.lib.getExe config.flake-root.package})" &&
                ${python}/bin/python -m scripts.missing_glyphs
              '';
            }
            {
              name = "fix-glyphs";
              help = "Convert glyphs to B/W PNGs and rename them to Unicode codepoints and names";
              command = ''
                cd "$(${pkgs.lib.getExe config.flake-root.package})" &&
                ${python}/bin/python -m scripts.fix_glyphs
              '';
            }
            {
              name = "make-specimens";
              help = "Make specimens of the glyphs for visual inspection";
              command = ''
                cd "$(${pkgs.lib.getExe config.flake-root.package})" &&
                ${pkgs.imagemagick}/bin/magick montage -background '#d0d0d0' -geometry +1+1 -tile 64x ${./glyphs/1x}/* specimen-1x.png &&
                ${pkgs.imagemagick}/bin/magick montage -background '#d0d0d0' -geometry +1+1 -tile 64x ${./glyphs/2x}/* specimen-2x.png &&
                ${pkgs.zopfli}/bin/zopflipng -y specimen-1x.png specimen-1x.png &&
                ${pkgs.zopfli}/bin/zopflipng -y specimen-2x.png specimen-2x.png
              '';
            }
          ];
        };
      };
    };
}
