{ pkgs ? import <nixpkgs> {} }:
let
	call = p: (import p) { inherit pkgs; };
in
{
	daemon = call ./daemon;

	prepare = call ./prepare;

	# Clients
	cli = call ./cli;
	discord = call ./discord;
}
