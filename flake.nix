{
  description = "Stockfish evaluation dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "aarch64-darwin";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.cairo
          pkgs.libxcb
        ];
        nativeBuildInputs = [
          pkgs.pkg-config
        ];
        shellHook = ''
          export PKG_CONFIG_PATH="${pkgs.cairo.dev}/lib/pkgconfig:${pkgs.libxcb.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
        '';
      };
    };
}