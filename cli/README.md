# Sonica CLI
Small command-line utility for Sonica. Similar to `mpc` in purpose, should be usable for automation, keybindings or quick control of music from a terminal. The CLI doesn't play music on its own, but connects to a running daemon.

## Building and Running
`nix-shell` is easiest, but otherwise just run with Python 3 after pulling in `grpcio` and `typer` with `pip -r requirements.txt`.
