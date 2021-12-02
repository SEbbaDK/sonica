{ pkgs ? import ../nixpkgs.nix {}
, grpc-tools ? pkgs.grpc-tools
, callPackage ? pkgs.callPackage
}:
pkgs.stdenv.mkDerivation rec {
    name = "sonica-prepare";

	pythonWithPackages = pkgs.python39.withPackages (pypkgs: with pypkgs; [
		typer
		grpcio
		grpcio-tools
	]);

	crystal-grpc = callPackage ./crystal-grpc.nix {};
	crystal-protobuf = callPackage ./crystal-protobuf.nix {};

    nativeBuildInputs = [
		grpc-tools

        crystal-grpc
        crystal-protobuf

		pythonWithPackages
    ];

    src = ./prepare.py;

	PROTOC_GEN_CRYSTAL = "${crystal-protobuf}/bin/protoc-gen-crystal";
	PROTOC_GEN_GRPC = "${crystal-grpc}/bin/grpc_crystal";

    dontUnpack = true;
    dontBuild = true;
    installPhase = ''
    	mkdir -p $out/bin
    	outfile=$out/bin/sonica-prepare

		echo '#!/bin/sh' > $outfile
       	echo 'PROTOC_GEN_CRYSTAL="${PROTOC_GEN_CRYSTAL}" \' >> $outfile
        echo 'PROTOC_GEN_GRPC="${PROTOC_GEN_GRPC}" \' >> $outfile
        echo 'PREPARE_PYTHON="${pythonWithPackages}/bin/python" \' >> $outfile
		echo "${pythonWithPackages}/bin/python $src \$@" >> $outfile

		chmod +x $outfile
    '';
}
