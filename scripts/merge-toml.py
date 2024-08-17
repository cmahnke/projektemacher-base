#!/usr/bin/env python

import os, io
import argparse, pathlib
import toml

defaultOutfile = "out.toml"

parser = argparse.ArgumentParser(prog="clean-toml.py", description="Remove duplicates from toml files")
parser.add_argument("files", type=pathlib.Path, help="Input file name(s)", nargs="+")
parser.add_argument("-o", "--output", help="Output file name, defaults to '{}'".format(defaultOutfile))
parser.add_argument("-d", "--delete", action="store_true", help="Remove input files")

args = parser.parse_args()

if args.files:
    parsed_toml = toml.load(args.files)

if args.delete:
    for file in args.files:
        file.unlink()

out = toml.dumps(parsed_toml)
if args.output and args.output != "-":
    with open(args.output, "w") as toml_file:
        toml_file.write(out)
else:
    print(out)
