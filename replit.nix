{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.python311Packages.pip
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
    pkgs.curl
    pkgs.bash
  ];
}
