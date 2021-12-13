{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
let
	sonica = import ../. { inherit pkgs; };
in
mkDerivation rec {
	name = "sonica-cli";

	python = pkgs.python39;
	pythonWithPackages = python.withPackages (pkg: with pkg; [
		grpcio
		typer
	]);

	buildInputs = [ sonica.prepare ];
	nativeBuildInputs = [ pythonWithPackages ];

	src = ./sonica-cli.py;

	dontUnpack = true;
	buildPhase = ''
		cp $src sonica-cli.py
		cp ${../sonica.proto} sonica.proto
		${sonica.prepare}/bin/sonica-prepare \
			--protofile sonica.proto \
			generate-grpc-python ./
	'';
	installPhase = ''
		mkdir -p $out/lib
		cp *.py $out/lib

		mkdir -p $out/bin
		outfile="$out/bin/sonica-cli"
		echo -e "#!/bin/sh\n${pythonWithPackages}/bin/python $out/lib/sonica-cli.py \$@" > $outfile
		chmod +x $outfile

		ln -s $outfile $out/bin/sc
	'';
}
