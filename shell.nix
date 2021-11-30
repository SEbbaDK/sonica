{ pkgs ? import <nixpkgs> {} }:
let
	sonica = import ./default.nix { inherit pkgs; };
in
pkgs.mkShell {
    name = "sonica-shell";

    buildInputs = [
		sonica.prepare
    ];
}
