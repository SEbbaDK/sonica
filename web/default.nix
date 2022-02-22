{ pkgs ? import <nixpkgs> {} }:
pkgs.stdenv.mkDerivation {
	name = "sonica-web";

	buildInputs = [
    	pkgs.elmPackages.elm
	];
}
