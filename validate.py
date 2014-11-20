#!/usr/bin/env python3

import logging
from xigt.codecs import xigtxml
from xigt.core import get_alignment_expression_ids as get_ae_ids

def must(condition, msg): test(condition, msg, logging.ERROR)
def should(condition, msg): test(condition, msg, logging.WARNING)
def may(condition, msg): test(condition, msg, logging.INFO)

def test(condition, msg, loglevel):
    if condition:
        logging.debug(msg)
    else:
        logging.log(loglevel, msg)
    return condition

def validate_corpus(igt):
    # validate_metadata
    ids = set()
    for igt in xc:
        should(
            igt.id is not None,
            "<igt> elements should have an id attribute."
        ) and must(
            igt.id not in ids,
            "Given ids of <igt> elements must be unique within a corpus."
        )
        ids.add(igt.id)
        validate_igt(igt)

def validate_igt(igt):
    # validate igt metadata
    item_ids = set([item.id for tier in igt for item in tier])
    ae_ids = chain.from_iterable([get_ae_ids(i.get_attribute(ra, default=""))
                                  for ra in reference_attributes])
    #must(ae_id in item_ids for ae_id in

def main(args):
    for f in args.files:
        with open(f, 'r') as fh:
            xc = xigtxml.load(fh, mode='transient')
            validate_corpus(xc)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Validate Xigt documents.")
    parser.add_argument('files', nargs='+')
    add('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    add('-q', '--quiet',
        action='store_const', const=0, dest='verbosity',
        help='Set verbosity to the quietest level.')

    args = parser.parse_args()
    logging.basicConfig(level=50-(args.verbosity*10))

    main(args)
