{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	pname = "sonica-cli";
	version = "0.1";

	python = pkgs.python39;
	pythonPackages = python.withPackages (pkg: with pkg; [
		grpcio
		typer
	]);

	nativeBuildInputs = [
		pythonPackages
	];
}
