#!/usr/bin/env python3

import argparse
import logging
import json

def run(args):
    infile = args.input
    outfile = args.output
    inp_format = args.format
    config = args.config
    if inp_format == 'toolbox':
        import xigt.importers.toolbox as importer
    elif inp_format == 'odin':
        import xigt.importers.odin as importer
    # elif ...
    if config is not None:
        config = json.load(open(config, 'r'))
    importer.xigt_import(infile, outfile, config)

def main(arglist=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    parser.add_argument('-i', '--input', metavar='PATH', required=True,
        help='The input corpus file or directory.')
    parser.add_argument('-o', '--output', metavar='PATH', required=True,
        help='The output Xigt corpus file or directory.')
    parser.add_argument('-f', '--format', metavar='FMT',
        choices=['toolbox', 'odin'], default='toolbox',
        help='The format of the input corpus (default: toolbox).')
    parser.add_argument('-c', '--config', metavar='PATH',
        help='A JSON-formatted configuration file for '
             'format-specific options.')
    args = parser.parse_args(arglist)
    logging.basicConfig(level=50-(args.verbosity*10))
    run(args)

if __name__ == '__main__':
    main()