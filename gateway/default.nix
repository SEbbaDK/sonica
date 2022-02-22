{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
, python ? pkgs.python39
}:

let
	sonica = import ../. { inherit pkgs; };
	pythonWithPackages = python.withPackages (pkg: with pkg; [
		grpcio
		websockets
		jsonschema
		typer
	]);
in
mkDerivation rec {
	name = "sonica-gateway";

	buildInputs = [ sonica.prepare ];
	nativeBuildInputs = [ pythonWithPackages ];

	src = ./.;

	dontUnpack = true;

	buildPhase = ''
		cp $src/*.py ./
		cp ${../sonica.proto} sonica.proto
		${sonica.prepare}/bin/sonica-prepare \
			--protofile sonica.proto \
			generate-grpc-python ./
	'';

	installPhase = ''
		mkdir -p $out/lib
		cp *.py $out/lib

		mkdir -p $out/bin
		outfile="$out/bin/sonica-gateway"
		echo -e "#!/bin/sh\n${pythonWithPackages}/bin/python $out/lib/sonica-gateway.py \$@" > $outfile
		chmod +x $outfile
	'';
}
