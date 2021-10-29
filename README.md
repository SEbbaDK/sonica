# Sonica - Central Music Player and Organizer
Sonica is a collection of software, that shares many similarities with the wonderful [mpd](https://github.com/MusicPlayerDaemon/MPD) and [mopidy](https://github.com/mopidy/mopidy). Sonica is also built up around a central daemon, but unlike the mpd architecture, does not assume that music is only located in one place or available through many platforms.

The goal of the Sonica project is to implement a music system that is collaborative-first, meaning party-play is assumed to be the primary means of use, but that also allows a single user to take advantage of the functionality without being burdened.

## Architecture
The core of Sonica is the [daemon](daemon/README.md) that implements a server following the [Sonica interface as defined by the gRPC spec](sonica.proto).

Client software then communicates with the daemon via gRPC (or in the case of the web-client, the generated HTTP REST interface). This allows easy creation of something like chat-bots in any language supported by gRPC, without writing a lot of boilerplate to interface with Sonica.

Each client and the daemon has their own README with build information and the like.

To work on *any* part of Sonica, the `prepare.py` script is needed to generate gRPC code for the language. To get started with the `discord` client, just run `./prepare.py discord`. 
This requires the python packages from the `requirements.txt` in the root, as well as `protoc` needing to be in the path. (Check the [gRPC web page](https://grpc.io/) for info on how to install it on your platform)
The easiest way to work on Sonica is to use the `nix` package manager, as all parts of Sonica has shells set up, so only `nix-shell` is needed for development.

