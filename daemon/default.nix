{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	name = "sonicad";

	python = pkgs.python39;
	pythonWithPkgs = python.withPackages (pkg: with pkg; [
    	connexion
		typer
		
		# Loading from youtube
		#youtube-dl
		#youtube-search
		# Loading from deezer
		deemix
		# Reading and writing tags
		pytaglib
		# Playing audio
		pydub
		simpleaudio
	]);

	nativeBuildInputs = [
		pythonWithPkgs
	];
}
