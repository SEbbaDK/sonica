{ pkgs ? import <nixpkgs> {}
, fetchFromGitHub ? pkgs.fetchFromGitHub
, crystal ? pkgs.crystal
}:
crystal.buildCrystalPackage rec {
    pname = "grpc-crystal";
    version = "2021-02-8";

    src = fetchFromGitHub {
        owner = "jgaskins";
        repo = "grpc";
        rev = "master";
        sha256 = "03ki01fc0vfp5xhkjrdqhlrrlmi85p00qyplfkjmd8cd78n8p47f";
    };

    format = "shards";
    lockFile = ./crystal-grpc-shard.lock;
    shardsFile = ./crystal-grpc-shards.nix;

	postInstall = ''
		echo "/ files"
		ls -lah
		echo "/bin files"
		ls -lah bin
	'';

	# Upstream has only a single failing-on-purpose test in the spec
    doCheck = false;
    doInstallCheck = false;
}
