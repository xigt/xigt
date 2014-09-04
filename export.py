#!/usr/bin/env python3

import logging
from xigt.codecs import xigtxml

def main(infile, outfile, out_format, replacements=None):
    if replacements:
        import json
        replacements = json.load(open(replacements,'r'))
    if out_format == 'latex':
        import xigt.exporters.latex as exporter
    # elif ...
    with open(infile, 'r') as in_fh, open(outfile, 'w') as out_fh:
        xc = xigtxml.load(in_fh, mode='transient')
        exporter.xigt_export(xc, out_fh, strmap=replacements)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    parser.add_argument('-i', '--input', metavar='PATH', required=True,
        help='The input Xigt corpus.')
    parser.add_argument('-o', '--output', metavar='PATH', required=True,
        help='The output corpus.')
    parser.add_argument('-f', '--format', metavar='FMT',
        choices=['latex'], default='latex',
        help='The format of the output corpus (default: latex).')
    parser.add_argument('-r', '--replacements', metavar='PATH',
        help='A tab-delimited file of replacement strings.')
    args = parser.parse_args()
    logging.basicConfig(level=50-(args.verbosity*10))
    main(args.input, args.output, args.format,
         replacements=args.replacements)