#!/usr/bin/env python

import sys
import os
from collections import defaultdict
import argparse
import logging

from xigt.codecs import xigtxml
from xigt import XigtCorpus, Igt, xigtpath as xp

def run(args):
    logging.debug('Partitioning with path \'{}\''.format(args.key_path))
    logging.debug('Writing to {}'.format(args.outdir))
    create_outdir(args.outdir)
    idx = defaultdict(lambda: defaultdict(set))  # key : filename : igt-index
    keypath = args.key_path
    for fn in args.infiles:
        logging.info('Indexing {}'.format(fn))
        index(fn, keypath, idx)
    for key, fn_idx in idx.items():
        logging.info('Writing {} (grouped from {} files)'
                     .format(key, len(fn_idx)))
        if key is None:
            key = args.default_key
        out_fn = os.path.join(args.outdir, normalize_key(key) + '.xml')
        write(out_fn, fn_idx)

def create_outdir(outdir):
    if os.path.isdir(outdir):
        logging.error('Output directory already exists.')
        sys.exit(1)
    try:
        os.mkdir(outdir)
    except OSError:
        logging.error('Output directory could not be created.')
        sys.exit(1)

def index(fn, by, idx):
    xc = xigtxml.load(fn, mode='transient')
    for i, igt in enumerate(xc):
        idx_key = xp.find(igt, by)
        idx[idx_key][fn].add(i)

def normalize_key(key):
    return key.replace(':', '-')

def write(out_fn, fn_idx):
    xc = XigtCorpus()
    for fn, igt_indices in fn_idx.items():
        # if possible, try to decode needed igts only and skip the rest
        in_xc = xigtxml.load(fn, mode='transient')
        # ignoring corpus-level metadata
        xc.extend(igt for i, igt in enumerate(in_xc) if i in igt_indices)
    # assume the nsmap of the first igt is the same for all
    if xc.igts: xc.nsmap = xc[0].nsmap
    xigtxml.dump(out_fn, xc)

def main(arglist=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Partition Xigt corpora",
        epilog='examples:\n'
            '    xigt partition --key-path=\'metadata//dc:subject/@olac:code\' by-lang *.xml\n'
            '    xigt partition --key-path=\'@doc-id\' by-doc-id by-lang/*.xml'
    )
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='increase the verbosity (can be repeated: -vvv)'
    )
    parser.add_argument('outdir',
        help='the output directory for partitioned files'
    )
    parser.add_argument('infiles',
        nargs='*',
        help='the Xigt corpus files to partition'
    )
    parser.add_argument('--key-path',
        metavar='XIGTPATH',
        help='the XigtPath query key (must result in a string, so it '
            'should end with an @attribute, text(), or value())'
    )
    parser.add_argument('--default-key',
        metavar='KEY', default='---',
        help='if --key-path fails, KEY is used instead (default: ---)'
    )
    args = parser.parse_args(arglist)
    logging.basicConfig(level=50-(args.verbosity*10))
    run(args)

if __name__ == '__main__':
    main()
