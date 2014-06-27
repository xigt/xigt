#!/usr/bin/env python3

import argparse
from xigt import XigtCorpus, Igt
from xigt.codecs import xigtxml

parser = argparse.ArgumentParser(description="Process Xigt documents.")
subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')
# separate tiers for standoff
sep_parser = subparsers.add_parser('s',
        help='extract tiers into separate files.')
sep_parser.add_argument('infile', help='Xigt data to process')
sep_parser.add_argument('-t', '--tiers', nargs='+',
        help='tiers to put into output file', required=True)
sep_parser.add_argument('-o', '--outfile', required=True)
sep_parser.add_argument('-r', '--remainder')
# merge tiers to combine annotations and source data
mrg_parser = subparsers.add_parser('m',
        help='merge tiers from separate files into a single corpus')
mrg_parser.add_argument('infile1', help='first Xigt corpus')
mrg_parser.add_argument('infile2', help='second Xigt corpus')
mrg_parser.add_argument('outfile', help='merged output Xigt corpus')
mrg_parser.add_argument('-O', '--overwrite', action='store_true',
        help='overwrite conflicting tiers in infile1 with those from infile2')

def separate_tiers(infile, tiers, outfile, remainderfile):
    tiers = set(tiers)
    # assuming XML for now
    with open(infile,'r') as instream:
        src_xc = xigtxml.load(instream)
        sep_xc = XigtCorpus(attributes=src_xc.attributes,
                            metadata=src_xc.metadata)
        for igt in src_xc.igts:
            sep_xc.add(Igt(id=igt.id, type=igt.type,
                           attributes=igt.attributes, metadata=igt.metadata,
                           tiers=[t for t in igt.tiers if t.type in tiers]))
        xigtxml.dump(open(outfile, 'w'), sep_xc, pretty_print=True)

    if not remainderfile: return
    with open(infile,'r') as instream:
        src_xc = xigtxml.load(instream)
        rem_xc = XigtCorpus(attributes=src_xc.attributes,
                            metadata=src_xc.metadata)
        for igt in src_xc.igts:
            rem_xc.add(Igt(id=igt.id, type=igt.type,
                           attributes=igt.attributes, metadata=igt.metadata,
                           tiers=[t for t in igt.tiers
                                  if t.type not in tiers]))
        xigtxml.dump(open(remainderfile, 'w'), rem_xc, pretty_print=True)

def merge_tiers(infile1, infile2, outfile, overwrite_tiers=False):
    raise NotImplementedError

if __name__ == '__main__':
    args = parser.parse_args()
    if args.cmd == 's':
        separate_tiers(args.infile, args.tiers, args.outfile, args.remainder)
