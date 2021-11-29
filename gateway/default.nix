{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
, python ? pkgs.python39
}:

mkDerivation rec {
	name = "sonica-gateway";

	pythonPackages = python.withPackages (pkg: with pkg; [
		grpcio
		websockets
		jsonschema
	]);

	nativeBuildInputs = [
		pythonPackages
	];
}
