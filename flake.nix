{
  description = "python implementation of wizard101's messaging system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts/";
    nix-systems.url = "github:nix-systems/default";
  };

  outputs = inputs @ { self, flake-parts, nix-systems, ... }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      debug = true;
      systems = import nix-systems;
      perSystem = {pkgs, self', ...}: {
        packages.wizmsg = pkgs.poetry2nix.mkPoetryApplication {
          projectDir = ./.;
        };
        packages.default = self'.packages.wizmsg;

        devShells.default = pkgs.mkShell {
          name = "wizmsg";
          packages = with pkgs; [poetry just alejandra black isort];
        };
      };
    };
}