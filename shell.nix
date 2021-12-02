{ pkgs ? import ./nixpkgs.nix {} }:
let
	sonica = import ./default.nix { inherit pkgs; };
in
pkgs.mkShell {
    name = "sonica-shell";

    nativeBuildInputs = [
    	sonica.daemon
    	sonica.prepare

    	sonica.cli
    	sonica.discord
    ];
}
