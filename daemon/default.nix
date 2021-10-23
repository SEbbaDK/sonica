{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	pname = "sonica-player";
	version = "0.1";

	python = pkgs.python39;
	pythonPackages = python.withPackages (pkg: with pkg; [
		grpcio
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
		pythonPackages
	];
}
