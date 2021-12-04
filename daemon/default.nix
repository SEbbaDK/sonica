{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
let
	sonica = import ../. { inherit pkgs; };
in
mkDerivation rec {
	name = "sonica-daemon";

	pythonWithPackages = pkgs.python39.withPackages (pkg: with pkg; [
		grpcio
		typer
		
		# Loading from youtube
		yt-dlp
		requests
		youtube-search
		ytmusicapi setuptools # the package isn't set up properly
		# Loading from deezer
		deemix
		# Reading and writing tags
		mutagen
		# Playing audio
		pydub
		simpleaudio
	]);

	buildInputs = [
    	sonica.prepare
	];

	nativeBuildInputs = [
		pythonWithPackages
	];

	src = ./.;

	buildPhase = ''
		cp ${../sonica.proto} sonica.proto
		${sonica.prepare}/bin/sonica-prepare \
			--protofile sonica.proto \
			generate-grpc-python ./
	'';
	
	installPhase = ''
		mkdir -p $out/lib
		cp -r *.py engines $out/lib/

		mkdir -p $out/bin
		bin=$out/bin/sonicad
		echo -e "#!/bin/sh\n${pythonWithPackages}/bin/python $out/lib/sonica-daemon.py \$@" > $bin
		chmod +x $bin
	'';
}
