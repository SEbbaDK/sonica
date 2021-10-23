{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	pname = "sonica-discord";
	version = "0.1";

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
