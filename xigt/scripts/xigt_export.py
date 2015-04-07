#!/usr/bin/env python3

import argparse
import logging
from xigt.codecs import xigtxml

def run(infile, outpath, out_format, config=None):
    cfg = None
    if config:
        import json
        cfg = json.load(open(config,'r'))
    if out_format == 'latex':
        import xigt.exporters.latex as exporter
    elif out_format == 'itsdb':
        import xigt.exporters.itsdb as exporter
    # elif ...
    with open(infile, 'r') as in_fh:
        xc = xigtxml.load(in_fh, mode='transient')
        exporter.xigt_export(xc, outpath, config=cfg)

def main(arglist=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    parser.add_argument('-i', '--input', metavar='PATH', required=True,
        help='The input Xigt corpus.')
    parser.add_argument('-o', '--output', metavar='PATH', required=True,
        help='The output corpus.')
    parser.add_argument('-f', '--format', metavar='FMT',
        choices=['latex', 'itsdb'], default='latex',
        help='The format of the output corpus (default: latex).')
    parser.add_argument('-c', '--config', metavar='PATH', default=None,
        help='A JSON-formatted configuration file.')
    args = parser.parse_args(arglist)
    logging.basicConfig(level=50-(args.verbosity*10))
    run(args.input, args.output, args.format, config=args.config)

if __name__ == '__main__':
    main()