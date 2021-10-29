# Sonica Daemon
The daemon is the central piece of the architecture, and is made up of the gRPC server, playlist functionality, local library management, and engines. Engines are modules that can perform searches and add songs to the library. This is useful for getting music from SoundCloud, Spotify as well as the local library to be available to all users.

## Building
Use `nix-shell` or install `libtaglib`/`taglib` via your package manager and use `pip -r requirements.txt` to get all necessary python packages.
