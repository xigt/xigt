#!/usr/bin/env python3

import logging
from xigt.codecs import xigtxml
from xigt.core import get_alignment_expression_ids as get_ae_ids

reference_attributes = ['alignment', 'segmentation', 'content']

def must(msg): return {'level': logging.ERROR, 'message': msg}
def should(msg): return {'level': logging.WARNING, 'message': msg}
def may(msg): return {'level': logging.INFO, 'message': msg}

# def must(condition, msg): test(condition, msg, logging.ERROR)
# def should(condition, msg): test(condition, msg, logging.WARNING)
# def may(condition, msg): test(condition, msg, logging.INFO)

# def test(condition, msg, loglevel):
#     if condition:
#         logging.debug(msg)
#     else:
#         logging.log(loglevel, msg)
#     return condition

def validate_corpus(xc):
    # validate_metadata
    records = []
    children = []
    ids = set()
    for i, igt in enumerate(xc):
        igtreport = validate_igt(igt, xc)
        igtreport['index'] = i

        if igt.id is not None and igt.id in ids:
            igtreport['records'].append(must(
                'The id attribute is not unique within the corpus.'
            ))
        ids.add(igt.id)

        children.append(igtreport)
    return {'records': records, 'children': children}

def validate_igt(igt, xc):
    records = []
    children = []
    report = {'records': records, 'children': children}

    if igt.id is None:
        records.append(should("No id is specified for the <igt> element."))
    else:
        report['id'] = igt.id

    # validate igt metadata

    ids = set()
    for i, tier in enumerate(igt):
        tierreport = validate_tier(tier, igt, xc)
        tierreport['index'] = i

        if tier.id is not None and tier.id in ids:
            tierreport['records'].append(must(
                'The id attribute is not unique within the <igt> element.'
            ))
        ids.add(tier.id)

        children.append(tierreport)

    return report

def validate_tier(tier, igt, xc):
    records = []
    children = []
    report = {'records': records, 'children': children}

    if tier.id is None:
        records.append(should("No id is specified for the <tier> element."))
    else:
        report['id'] = tier.id

    if tier.type is None:
        records.append(should("No type is specified for the <tier> element."))

    for refattr in reference_attributes:
        if refattr in tier.attributes and igt.get(tier.attributes[refattr]) is None:
            records.append(must(
                "Reference attribute {} does not select an id from an "
                "existing <tier> in the <igt>."
            ))

    # validate tier metadata

    ids = set()
    for i, item in enumerate(tier):
        itemreport = validate_item(item, tier, igt, xc)
        itemreport['index'] = i

        # TODO: move this to IGT level
        if item.id is not None and item.id in ids:
            itemreport['records'].append(must(
                'The id attribute is not unique within the <igt> element.'
            ))
        ids.add(item.id)

        children.append(itemreport)

    return report


def validate_item(item, tier, igt, xc):
    return {'records': [], 'children': []}
    #should(item.id is not None, "<item> elements should have an id attribute.")
    #for refattr in reference_attributes:


def print_report(report):
    for record in report.get('records', []):
        logging.log(record['level'], record['message'])
        for child in report.get('children', []):
            print_report(child)


def main(args):
    for f in args.files:
        with open(f, 'r') as fh:
            xc = xigtxml.load(fh, mode='transient')
            report = validate_corpus(xc)
            print_report(report)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Validate Xigt documents.")
    add = parser.add_argument
    add('files', nargs='+')
    add('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    add('-q', '--quiet',
        action='store_const', const=0, dest='verbosity',
        help='Set verbosity to the quietest level.')

    args = parser.parse_args()
    logging.basicConfig(
        level=50-(args.verbosity*10),
        format='%(levelname)s %(message)s'
    )

    main(args)
