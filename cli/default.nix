{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	name = "sonica-cli";

	python = pkgs.python39;
	pythonPackages = python.withPackages (pkg: with pkg; [
		grpcio
		typer
	]);

	nativeBuildInputs = [
		pythonPackages
	];
}
