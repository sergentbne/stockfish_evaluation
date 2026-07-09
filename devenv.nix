{ pkgs, lib, config, inputs, ... }:
{
	packages = [
	  pkgs.cairo
	  pkgs.libxcb
	  pkgs.gcc
	  pkgs.pkg-config
	];
  cachix.enable = false;
  languages.python = {
    enable = true;
    # version = "3.12"; 
  };
}
