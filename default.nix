{ pkgs ? import ./nixpkgs.nix {} }:
let
	call = p: (import p) { inherit pkgs; };
in
rec {
	daemon = call ./daemon;

	prepare = call ./prepare;

	python_grpc = pkgs.stdenv.mkDerivation {
		name = "sonica-python-grpc";
		src = ./sonica.proto;
		buildInputs = [ prepare ];
		dontUnpack = true;

		buildPhase = ''
			cp $src sonica.proto
			sonica-prepare \
				--protofile sonica.proto \
				generate-grpc-python ./
		'';
		installPhase = ''
			mkdir -p $out/lib
			cp *.py $out/lib
		'';
	};

	# Clients
	cli = call ./cli;
	discord = call ./discord;
}
