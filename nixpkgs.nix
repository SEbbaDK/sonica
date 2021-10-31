let
    rev = "930da485d9af8100f8858bd6fe8f28e3eca26933";
    hash = "1x1ksjz6ag83nnsc1z8liw5sbgxi95lk1j58k3wnjnsx3dhca961";
in
import (fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/${rev}.tar.gz";
    sha256 = hash;
})
