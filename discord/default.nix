{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
let
	sonica = import ../. { inherit pkgs; };
in
mkDerivation rec {
	name = "sonica-discord";

	python = pkgs.python39;
	pythonWithPackages = python.withPackages (pkg: with pkg; [
		grpcio
		discordpy
		typer
	]);

	buildInputs = [ sonica.prepare ];
	nativeBuildInputs = [ pythonWithPackages ];

	src = ./sonica-discord.py;

	dontUnpack = true;

	buildPhase = ''
		cp ${../sonica.proto} sonica.proto
		${sonica.prepare}/bin/sonica-prepare \
			--protofile sonica.proto \
			generate-grpc-python ./
	'';

	installPhase = ''
		mkdir -p $out/lib
		cp *.py $out/lib/
		mainfile="$out/lib/sonica-discord.py"
		cp $src $mainfile

		mkdir -p $out/bin/
		outfile="$out/bin/sonica-discord"
		echo -e "#!/bin/sh\n${pythonWithPackages}/bin/python $mainfile \$@" > $outfile
		chmod +x $outfile
	'';
}
