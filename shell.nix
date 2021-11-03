{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell rec {
    name = "sonica-shell";

	python = pkgs.python39.withPackages (pypkgs: map (p: pypkgs.${p}) pythonPackages);
	pythonPackages = [
		"typer"
		"pyyaml"
	];

    buildInputs = [
        python
		pkgs.openapi-generator-cli
    ];
}
