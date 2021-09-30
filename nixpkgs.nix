let
    rev = "f05192f5d7b77d70f3b4b979b9466a9e7b0d445a";
    hash = "1a5kazsi00bwmsrj75paif9hyrkdnm61gll1qqs2mwyfmhhcllj6";
in
import (fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/${rev}.tar.gz";
    sha256 = hash;
})
