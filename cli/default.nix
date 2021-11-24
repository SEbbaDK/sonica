{ pkgs ? import ../nixpkgs.nix { }
, mkDerivation ? pkgs.stdenv.mkDerivation
}:
mkDerivation rec {
	name = "sonicac";

	buildInputs = with pkgs; [
    	shards
    	crystal
    	pkg-config
    	openssl
    	openssl.out
	];
}
