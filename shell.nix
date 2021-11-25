{ pkgs ? import <nixpkgs> {}
, grpc-tools ? pkgs.grpc-tools
, callPackage ? pkgs.callPackage
, protoc-gen-go-grpc ? pkgs.protoc-gen-go-grpc
, protoc-gen-go ? pkgs.protoc-gen-go
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

        protoc-gen-go
        protoc-gen-go-grpc

		(pkgs.python39.withPackages (pypkgs:
			map (p: pypkgs.${p}) pythonPackages
		))

    ];

	PROTOC_GEN_CRYSTAL = "${crystal-protobuf}/bin/protoc-gen-crystal";
	PROTOC_GEN_GRPC = "${crystal-grpc}/bin/grpc_crystal";
    PROTOC_GEN_GO = "${protoc-gen-go}/bin/protoc-gen-go";
    PROTOC_GEN_GO_GRPC = "${protoc-gen-go-grpc}/bin/protoc-gen-go-grpc";
}
