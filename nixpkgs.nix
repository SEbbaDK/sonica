let
    rev = "930da485d9af8100f8858bd6fe8f28e3eca26933";
    hash = "1a5kazsi00bwmsrj75paif9hyrkdnm61gll1qqs2mwyfmhhcllj6";
in
import (fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/${rev}.tar.gz";
    sha256 = hash;
})
