# Sonica Discord
The [Discord](https://discord.com/) client was the original interface for Sonica, and existed before the current architecture was set up. Originally it ran as a 150 line python hack on top of MPD, but it was too inflexible and frequently broke.
The current implementation is very simple as all work is done by the daemon.

## Building
Use `nix-shell` or run `pip -r requirements.txt` to get all necessary python packages.
Remember that a running daemon is needed for any client to work.

