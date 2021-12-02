let
    rev = "716815ce2a1fcb135843c7441648a59d62fb6eb6";
    hash = "1x1ksjz6ag83nnsc1z8liw5sbgxi95lk1j58k3wnjnsx3dhca961";
in
import (fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/${rev}.tar.gz";
    sha256 = hash;
})
