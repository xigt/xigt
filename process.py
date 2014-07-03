#!/usr/bin/env python3

import argparse
import os.path
from collections import defaultdict
from xigt import XigtCorpus, Igt
from xigt.codecs import xigtxml


def divide_corpus(args):
    infile = args.infile
    outdir = args.outdir
    igt_index = 0
    indices = set()

    def make_filename(fn):
        return os.path.join(outdir, fn + '.xml')

    # this should make reading the corpus faster
    def selective_decode_igt(elem):
        nonlocal igt_index, indices
        if igt_index not in indices:
            igt = None
        else:
            igt = xigtxml.default_decode_igt(elem)
            indices.remove(igt_index)
        igt_index += 1
        return igt

    if args.meta is not None:
        metatype, func = args.meta
        func = eval('lambda m:{}'.format(func))
        get_key = lambda igt: next(
            (func(m) for m in igt.get_meta(metatype) if m is not None),
            None
        )

    # get a mapping of code to the indexed position of each IGT
    keymap = defaultdict(set)
    xc = xigtxml.load(open(infile, 'r'), mode='transient')
    for i, igt in enumerate(xc):
        key = get_key(igt)
        keymap[key].add(i)

    xigtxml.decode_igt = selective_decode_igt

    # now group IGTs with similar languages into a file
    for key, indices in keymap.items():
        if key is None:
            key = '-others-'  # FIXME not guaranteed to be unique
        igt_index = 0
        xc = xigtxml.load(open(infile, 'r'), mode='transient')
        xigtxml.dump(open(make_filename(key), 'w'), xc)


def separate_tiers(args):
    tiers = set(args.tiers)
    # assuming XML for now
    with open(args.infile,'r') as instream:
        src_xc = xigtxml.load(instream)
        sep_xc = XigtCorpus(attributes=src_xc.attributes,
                            metadata=src_xc.metadata)
        for igt in src_xc.igts:
            sep_xc.add(Igt(id=igt.id, type=igt.type,
                           attributes=igt.attributes, metadata=igt.metadata,
                           tiers=[t for t in igt.tiers if t.type in tiers]))
        xigtxml.dump(open(args.outfile, 'w'), sep_xc, pretty_print=True)

    if not args.remainder: return
    with open(args.infile,'r') as instream:
        src_xc = xigtxml.load(instream)
        rem_xc = XigtCorpus(attributes=src_xc.attributes,
                            metadata=src_xc.metadata)
        for igt in src_xc.igts:
            rem_xc.add(Igt(id=igt.id, type=igt.type,
                           attributes=igt.attributes, metadata=igt.metadata,
                           tiers=[t for t in igt.tiers
                                  if t.type not in tiers]))
        xigtxml.dump(open(args.remainder, 'w'), rem_xc, pretty_print=True)


def merge_tiers(infile1, infile2, outfile, overwrite_tiers=False):
    raise NotImplementedError


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process Xigt documents.")
    subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')
    # place IGTs into subcorpora based on a property
    div_parser = subparsers.add_parser(
        'divide', aliases=['d'],
        help='Divide a corpus into subcorpora by some condition.'
    )
    div_parser.set_defaults(func=divide_corpus)
    div_parser.add_argument(
        '-o', '--outdir', required=True, help='Output directory.'
    )
    div_parser.add_argument(
        '-i', '--infile', required=True, help='Input corpus file.'
    )
    div_parser.add_argument(
        '-m', '--meta',
        metavar=('TYPE', 'FUNC'), nargs=2, required=True,
        help='Divide by the <meta type="TYPE"> element using the key '
             'returned by FUNC(m), where m is the parsed meta object. '
             'Returns the first non-None value returned (otherwise None). '
             'E.g. --meta language "m.attributes.get(\'iso-639-3\') '
             'if \'phrases\' in m.attributes.get(\'tiers\',\'\') else None"'
    )
    # split parts of IGTs into separate corpora
    sep_parser = subparsers.add_parser(
        's',
        help='Extract tiers into separate files.'
    )
    sep_parser.set_defaults(func=separate_tiers)
    sep_parser.add_argument('infile', help='Xigt data to process')
    sep_parser.add_argument('-t', '--tiers', nargs='+',
            help='tiers to put into output file', required=True)
    sep_parser.add_argument('-o', '--outfile', required=True)
    sep_parser.add_argument('-r', '--remainder')
    # merge tiers to combine annotations and source data
    mrg_parser = subparsers.add_parser(
        'm',
        help='Merge tiers from separate files into a single corpus.')
    mrg_parser.add_argument('infile1', help='first Xigt corpus')
    mrg_parser.add_argument('infile2', help='second Xigt corpus')
    mrg_parser.add_argument('outfile', help='merged output Xigt corpus')
    mrg_parser.add_argument('-O', '--overwrite', action='store_true',
            help='overwrite conflicting tiers in infile1 with those from infile2')
    args = parser.parse_args()
    args.func(args)