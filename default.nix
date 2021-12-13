{ pkgs ? import ./nixpkgs.nix {} }:
let
	call = p: (import p) { inherit pkgs; };
in
rec {
	daemon = call ./daemon;
	gateway = call ./gateway;

	prepare = call ./prepare;

	# Clients
	cli = call ./cli;
	discord = call ./discord;
}
