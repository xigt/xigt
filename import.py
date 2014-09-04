#!/usr/bin/env python3

import logging

def main(infile, outfile, inp_format):
    if inp_format == 'toolbox':
        import xigt.importers.toolbox as importer
    # elif ...
    with open(infile, 'r') as in_fh, open(outfile, 'w') as out_fh:
        importer.xigt_import(in_fh, out_fh)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    parser.add_argument('-i', '--input', metavar='PATH', required=True,
        help='The input corpus.')
    parser.add_argument('-o', '--output', metavar='PATH', required=True,
        help='The output Xigt corpus.')
    parser.add_argument('-f', '--format', metavar='FMT',
        choices=['toolbox'], default='toolbox',
        help='The format of the input corpus (default: toolbox).')
    args = parser.parse_args()
    logging.basicConfig(level=50-(args.verbosity*10))
    main(args.input, args.output, args.format)