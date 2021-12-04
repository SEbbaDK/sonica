{ pkgs ? import ./nixpkgs.nix {} }:
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
