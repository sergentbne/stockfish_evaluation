{
  description = "Stockfish evaluation dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];
      each_system = f: nixpkgs.lib.genAttrs systems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        f {
          inherit pkgs system;
        }
      );
    in
    {
      devShells = each_system ({ pkgs, system }: {
        default = pkgs.mkShell {
          packages = [
            pkgs.cairo
            pkgs.libxcb
            pkgs.gcc
            pkgs.pkg-config
            pkgs.uv
          ];
          shellHook = ''
            export PKG_CONFIG_PATH="${pkgs.cairo.dev}/lib/pkgconfig:${pkgs.libxcb.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
            export DYLD_FALLBACK_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [pkgs.cairo pkgs.stdenv.cc.cc]}:$DYLD_FALLBACK_LIBRARY_PATH"
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [pkgs.cairo pkgs.stdenv.cc.cc]}:$LD_LIBRARY_PATH"
          '';
        };
      });
    };
}
