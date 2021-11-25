{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	name = "sonica-daemon";

	python = pkgs.python39;
	pythonPackages = python.withPackages (pkg: with pkg; [
		grpcio
		typer
		
		# Loading from youtube
		youtube-dl
		#youtube-search
		ytmusicapi setuptools # the package isn't set up properly
		# Loading from deezer
		deemix
		# Reading and writing tags
		pytaglib
		# Playing audio
		pydub
		simpleaudio
	]);

	nativeBuildInputs = [
		pythonPackages
	];
}
