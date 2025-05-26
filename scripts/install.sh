#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$(realpath "$SCRIPT_DIR/..")
STD_FILEPATH="$ROOT_DIR/std-library/std.basic"
INSTALL_PATH="/usr/local/include/tbasic"

echo "Installing STD library..."
mkdir -p "$INSTALL_PATH"
cp "$STD_FILEPATH" "$INSTALL_PATH"
echo "STD library installed"