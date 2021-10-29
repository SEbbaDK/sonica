{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation

# Dependencies
, crystal ? pkgs.crystal
, shards ? pkgs.shards
, pkg-config ? pkgs.pkg-config
, openssl ? pkgs.openssl
, crystal2nix ? pkgs.crystal2nix
, buildCrystalPackage ? pkgs.crystal.buildCrystalPackage
, ...
}:
let
	shard = builtins.readFile ./shard.yml;
	version = builtins.head (builtins.match ".*version: ([0-9.]+).*" shard);
in
(buildCrystalPackage rec {
	pname = "sonica-cli";
	inherit version;

	buildInputs = [ openssl openssl.out ];
	srcs = [
		./shard.yml
		./sonica-cli.cr

		./sonica.pb.cr
		./sonica_services.pb.cr
	];

	unpackPhase = ''
		ls -lah
		for f in $srcs
		do
			cp "$f" ./
		end
	'';

	format = "shards";
	lockFile = ./shard.lock;
	shardsFile = ./shards.nix;

	# Disable tests until they work
	doCheck = false;
	doInstallCheck = false;
})
