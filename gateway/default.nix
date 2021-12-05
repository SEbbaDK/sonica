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
	]);
in
mkDerivation rec {
	name = "sonica-gateway";

	nativeBuildInputs = [
		pythonWithPackages
	];

	src = (builtins.filterSource
		(path: type: builtins.elem (baseNameOf path) [
			"gateway.py"
			"methods.py"
			"validate.py"
		])) ./.;

	dontUnpack = true;
	dontBuild = true;

	wrapper = pkgs.writeText "wrapper" ''
#!/bin/sh
export PYTHONPATH=${sonica.python_grpc}/lib
${pythonWithPackages}/bin/python ..cd /lib/gateway.py $@
'';

	installPhase = ''
		mkdir -p $out/lib
		cp $src/*.py $out/lib

		mkdir -p $out/bin
		cat > $out/bin/sonicagw << END_SCRIPT
#!/usr/bin/bash
export PYTHONPATH=${sonica.python_grpc}/lib
${pythonWithPackages}/bin/python $out/lib/gateway.py $@
END_SCRIPT
		chmod +x $out/bin/sonicagw
	'';
}
