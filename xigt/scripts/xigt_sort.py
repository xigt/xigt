#!/usr/bin/env python

from __future__ import print_function
import re
import argparse
import logging

from xigt.codecs import xigtxml
from xigt import XigtCorpus, Igt, xigtpath as xp

def run(args):
    xc = xigtxml.load(args.infile)
    if args.igt_key:
        xc._list.sort(key=make_sortkey(args.igt_key))
    if args.tier_key:
        for igt in xc:
            igt._list.sort(key=make_sortkey(args.tier_key))
    if args.item_key:
        for igt in xc:
            for tier in igt:
                tier._list.sort(key=make_sortkey(args.item_key))
    if args.in_place:
        xigtxml.dump(args.infile, xc)
    else:
        print(xigtxml.dumps(xc))

def make_sortkey(sortkeys):
    # return int values if possible (for int comparison), otherwise strings
    def safe_int(x):
        try:
            return int(x)
        except ValueError:
            return x
    key = lambda x: [k for sk in sortkeys
                     for k in map(safe_int,
                                  re.split(r'(\d+)', xp.find(x, sk) or ''))]
    return key

def main(arglist=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Sort Igts, Tiers, or Items in Xigt corpora",
        epilog='examples:\n'
            '    xigt sort --igt-key=\'@doc-id\' --igt-key=\'@id\' in.xml > out.xml\n'
            '    xigt sort --tier-key=\'@type\' in.xml > out.xml'
    )
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='increase the verbosity (can be repeated: -vvv)'
    )
    parser.add_argument('infile',
        help='the Xigt corpus file to sort'
    )
    parser.add_argument('--in-place',
        action='store_true',
        help='don\'t print to stdout; modify the input file in-place'
    )
    parser.add_argument('--igt-key',
        metavar='XIGTPATH', action='append',
        help='the XigtPath query for IGTs (must result in a string, so '
            'it should end with an @attribute, text(), or value())'
    )
    parser.add_argument('--tier-key',
        metavar='XIGTPATH', action='append',
        help='the XigtPath query for Tiers (must result in a string, so '
            'it should end with an @attribute, text(), or value())'
    )
    parser.add_argument('--item-key',
        metavar='XIGTPATH', action='append',
        help='the XigtPath query for Items (must result in a string, so '
            'it should end with an @attribute, text(), or value())'
    )
    # parser.add_argument('--tier-deps',
    #     action='store_true',
    #     help='sort tiers by reference dependencies'
    # )
    # parser.add_argument('--item-deps',
    #     action='store_true',
    #     help='sort items by reference dependencies'
    # )
    args = parser.parse_args(arglist)
    logging.basicConfig(level=50-(args.verbosity*10))
    run(args)

if __name__ == '__main__':
    main()
