{ pkgs ? import <nixpkgs> {}
, mkDerivation ? pkgs.stdenv.mkDerivation
, fetchFromGitHub ? pkgs.fetchFromGitHub
, crystal ? pkgs.crystal
}:
mkDerivation rec {
    pname = "crystal-protobuf";
    version = "v2.2.3";

    src = fetchFromGitHub {
        owner = "jeromegn";
        repo = "protobuf.cr";
        rev = version;
        sha256 = "05dmvypcsmzcqapim5kngigkknfril40l2bwmvb5fh6fzm8ji7ga";
    };

    buildInputs = [
        crystal
    ];

    buildPhase = ''
		crystal build bin/protoc-gen-crystal.cr
    '';

    installPhase = ''
    	mkdir -p $out/bin
    	mv protoc-gen-crystal $out/bin/
	'';
}
