{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	name = "sonica-discord";

	python = pkgs.python39;
	pythonPackages = python.withPackages (pkg: with pkg; [
		grpcio
		discordpy
		typer
	]);

	nativeBuildInputs = [
    	pythonPackages
	];
}
