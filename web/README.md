# Sonica Web
Sonica Web is a graphical web-based client for interacting with Sonica.
It currently relies on a connection to the [Sonica Gateway](../gateway), which will have to be set up and running alongside the [daemon](../daemon).

The current version of the web interface is a minimal client, containing playback controls, search/queuing and a status display.

## Building
Sonica Web is built with [Elm](https://elm-lang.org/), so the tooling for elm is required.
Running the [`build.sh`](./build.sh) script should build the application, and the [`index.html`](./index.html) can then be opened in a webbrowser (assuming both the daemon and gateway is running).

