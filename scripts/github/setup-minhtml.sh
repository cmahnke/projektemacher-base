#!/usr/bin/env bash

set -e -o pipefail

cargo install minhtml

sudo cp $HOME/.cargo/bin/minhtml /usr/local/bin/
