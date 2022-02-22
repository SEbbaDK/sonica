let
    rev = "c03431640e3cc3c597f4d786f573970577709097";
    hash = "0fqil5m81vc9dq2p44gczqx31zclk7knka3lq5j6cxpm4vlbb0r0";
in
import (fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/${rev}.tar.gz";
    sha256 = hash;
})
