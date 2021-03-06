![Sonica](./media/banner.png)

# Sonica - Central Music Player and Organizer
Sonica is a collection of software, that shares many similarities with the wonderful [mpd](https://github.com/MusicPlayerDaemon/MPD) and [mopidy](https://github.com/mopidy/mopidy). Sonica is also built up around a central daemon, but unlike the mpd architecture, does not assume that music is only located in one place or available through many platforms.

The goal of the Sonica project is to implement a music system that is collaborative-first, meaning party-play is assumed to be the primary means of use, but that also allows a single user to take advantage of the functionality without being burdened.

## Architecture
The core of Sonica is the [daemon](daemon/README.md) that implements a server following the [Sonica interface as defined by the gRPC spec](sonica.proto).

Client software then communicates with the daemon via gRPC (or in the case of the web-client, the generated HTTP REST interface). This allows easy creation of something like chat-bots in any language supported by gRPC, without writing a lot of boilerplate to interface with Sonica.

Each client and the daemon has their own README with build information and the like.

## Installation
Currently Sonica is only pre-packaged for use with nix.
To install it via nix, the repo has a root map of tools:

```nix
sonica = import (fetchTarball "https://github.com/SEbbaDK/sonica/archive/v0.2.tar.gz) { };
# Then sonica.cli, sonica.daemon, etc. is packages that can be imported into a shell
```

This also means you can try different features out with:

```nix
nix run -f "https://github.com/sebbadk/sonica/archive/master.tar.gz" cli
```

Directly installing with nixos it could be done as:

```nix
let
	sonica = import (fetchTarball "https://github.com/SEbbaDK/sonica/archive/v0.2.tar.gz) { };
in
{
	environment.systemPackages [ sonica.daemon sonica.cli ];
}
```

## Build instructions 
To work on *any* part of Sonica, the `prepare.py` script is needed to generate gRPC code for the language. To get started with the `discord` client, just run `./prepare/prepare.py discord`. 
This requires the python packages from the `prepare/requirements.txt`, as well as `protoc` needing to be in the path. (Check the [gRPC web page](https://grpc.io/) for info on how to install it on your platform)
The easiest way to work on Sonica is to use the `nix` package manager, as all parts of Sonica has shells set up, so only `nix-shell` is needed for development. For preparation, use `nix-shell` in the root and then `sonica-prepare` will be in your path.

### Arch-specific instructions
To get everything working on Arch and Arch-derived distributions, follow the following steps:

1. Install the `crystal` and `shards` packages from the Arch repositories
2. In a terminal, navigate to the root directory of the Sonica repo
3. Run `shards init`
4. Run `echo -e "dependencies:\n\tlogger:\n\t\tgithub: crystal-lang/logger.cr\n\tgrpc:\n\t\tgithub: jgaskins/grpc" >> shard.yml`
5. Run `shards install` and then restart your shell

From here, you can start install requirements and preparing specific installation modules. For python-based modules (such as `discord` and `daemon`):
1. Run `python -m venv venv`, and then active the virtual environment, if you want to use a virtual environment.
2. Run `python -m pip install --upgrade pip` followed by `pip install -r prepare/requirements.txt`
3. For each `[MODULE]` you wish to work on, run `pip install -r [MODULE]/requirements.txt`, then `python prepare/prepare.py --protoc-gen-crystal ./bin/protoc-gen-crystal --protoc-gen-grpc ./bin/grpc_crystal [MODULE]`
