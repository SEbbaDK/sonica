{ pkgs ? import ./nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
, python ? pkgs.python39
}:
mkDerivation {
	pname = "sonica";
	version = "0.1";

	nativeBuildInputs = [
		(python.withPackages (pkg: with pkg; [
			typer
			youtube-dl
			youtube-search
			discordpy
			playsound
			deemix
			pytaglib
		]))
	];
}
