{ pkgs ? import <nixpkgs> {}
, grpc-tools ? pkgs.grpc-tools
, callPackage ? pkgs.callPackage
}:
let
	grpc = callPackage ./grpc/shell.nix {};
in
pkgs.mkShell rec {
    name = "sonica-shell";

	pythonPackages = [
		"typer"
		"grpcio"
		"grpcio-tools"
	];

	crystal-grpc = callPackage ./nix/crystal-grpc.nix {};
	crystal-protobuf = callPackage ./nix/crystal-protobuf.nix {};

    buildInputs = [

		grpc-tools

        crystal-grpc
        crystal-protobuf

		(pkgs.python39.withPackages (pypkgs:
			map (p: pypkgs.${p}) pythonPackages
		))

    ];

	PROTOC_GEN_CRYSTAL = "${crystal-protobuf}/bin/protoc-gen-crystal";
	PROTOC_GEN_GRPC = "${crystal-grpc}/bin/grpc_crystal";
}
