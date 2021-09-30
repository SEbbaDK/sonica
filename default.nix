{ pkgs ? import ./nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
, python ? pkgs.python39
}:
mkDerivation {
	pname = "sonica";
	version = "0.1";

	nativeBuildInputs = [
		(python.withPackages (pkg: with pkg; [
    		# CLI library
			typer
			# Discord bot lib
			discordpy
			# Loading from youtube
			youtube-dl
			youtube-search
			# Loading from deezer
			deemix
			# Reading and writing tags
			pytaglib
			# Playing audio
			pydub
			simpleaudio
		]))
	];
}
