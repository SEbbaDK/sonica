let
    rev = "716815ce2a1fcb135843c7441648a59d62fb6eb6";
    hash = "0qhjj4c6jx2s2da6zch2mfy0q7iwz3flpik4w4vw7bag3k26ia6k";
in
import (fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/${rev}.tar.gz";
    sha256 = hash;
})
