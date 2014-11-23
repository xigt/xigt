#!/usr/bin/env python3

import logging
import warnings
warnings.simplefilter('ignore')

from xigt.codecs import xigtxml
from xigt.core import get_alignment_expression_ids as get_ae_ids

datalevels = ['corpus', 'igt', 'tier', 'item']
reference_attributes = ['alignment', 'segmentation', 'content']


# VALIDATORS

def validate_corpus(xc):
    # validate_metadata
    records = []
    children = []
    report = {'records': records, 'children': children, 'id': xc.id}

    ids = set()
    for i, igt in enumerate(xc):
        igtreport = validate_igt(igt, xc)
        igtreport['index'] = i
        test_unique_id(igt, ids, 'corpus', igtreport)

        report['children'].append(igtreport)

    return report


def validate_igt(igt, xc):
    records = []
    children = []
    report = {'records': records, 'children': children, 'id': igt.id}

    test_has_id(igt, '<igt>', report)

    # validate igt metadata

    tier_ids = set()
    item_ids = set()
    for i, tier in enumerate(igt):
        tierreport = validate_tier(tier, igt, xc)
        tierreport['index'] = i

        # tier and item IDs must be unique within an IGT
        test_unique_id(tier, tier_ids, '<igt>', tierreport)
        for itm, itmrep in zip(tier.items, tierreport.get('children', [])):
            test_unique_id(itm, item_ids, '<igt>', itmrep)

        report['children'].append(tierreport)

    return report


def validate_tier(tier, igt, xc):
    records = []
    children = []
    report = {'records': records, 'children': children, 'id': tier.id}

    test_has_id(tier, '<tier>', report)
    test_has_type(tier, '<tier>', report)
    test_refattr_in_igt(tier, igt, report)


    # validate tier metadata

    ids = set()
    for i, item in enumerate(tier):
        itemreport = validate_item(item, tier, igt, xc)
        itemreport['index'] = i

        test_unique_id(item, ids, '<tier>', itemreport)

        report['children'].append(itemreport)

    return report


def validate_item(item, tier, igt, xc):
    report = {'records': [], 'id': item.id}
    test_has_id(item, '<item>', report)
    test_refattr_in_aligned_tier(item, tier, igt, report)
    #should(item.id is not None, "<item> elements should have an id attribute.")
    #for refattr in reference_attributes:
    return report


# TEST HELPERS

def must(msg): return {'level': logging.ERROR, 'message': msg}
def should(msg): return {'level': logging.WARNING, 'message': msg}
def may(msg): return {'level': logging.INFO, 'message': msg}


# TEST FUNCTIONS

def test_has_id(obj, datalevel, report):
    if not hasattr(obj, 'id') or obj.id is None:
        report['records'].append(should(
            'No id is specified for the {} element.'.format(datalevel)
        ))

def test_unique_id(obj, idset, scope, report):
    if hasattr(obj, 'id') and obj.id is not None:
        if obj.id in idset:
            report['records'].append(must(
                'The id attribute is not unique within the {}.'
                .format(scope)
            ))
        idset.add(obj.id)

def test_has_type(obj, datalevel, report):
    if not hasattr(obj, 'type') or obj.type is None:
        report['records'].append(should(
            'No type is specified for the {} element.'.format(datalevel)
        ))

def test_refattr_in_igt(tier, igt, report):
    for ref in reference_attributes:
        if ref not in tier.attributes:
            continue
        id = tier.attributes[ref]
        if igt.get(id) is None:
            report['records'].append(must(
                'Reference attribute "{}" selects an unavailable id ("{}")'
                .format(ref, id)
            ))

def test_refattr_in_aligned_tier(item, tier, igt, report):
    for ref in reference_attributes:
        if ref not in item.attributes:
            continue
        if ref not in tier.attributes or igt.get(tier.attributes[ref]) is None:
            continue  # this is already checked by test_refattr_in_tier()
        reftier = igt.get(tier.attributes[ref])
        for id in get_ae_ids(item.attributes[ref]):
            if reftier.get(id) is None:
                report['records'].append(must(
                    'Reference attribute "{}" selects an unavailable id ("{}")'
                    .format(ref, id)
                ))

def test_overlapping_ae(item, report):
    for ref in reference_attributes:
        if ref not in item.attributes:
            continue


# FILTERING

def report_is_empty(report):
    return not any(report.get('records', []) + report.get('children', []))

def filter_empty_reports(report):
    report['children'] = [filter_empty_reports(child)
                          for child in report.get('children', [])]
    if report_is_empty(report):
        report = {}
    return report

# FORMATTING AND PRINTING

def print_report(report, args, nestlevel=0):
    if report_is_empty(report):
        return
    print(format_heading(report, nestlevel, args))
    for record in report.get('records', []):
        msg = format_message(record, nestlevel, args)
        logging.log(record['level'], msg)
    for child in report.get('children', []):
        print_report(child, args, nestlevel+1)

# coloring inspired by: http://stackoverflow.com/a/384125/1441112

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#These are the sequences needed to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[3%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    logging.DEBUG: COLOR_SEQ % BLUE,
    logging.INFO: COLOR_SEQ % WHITE,
    logging.WARNING: COLOR_SEQ % YELLOW,
    logging.ERROR: COLOR_SEQ % RED,
    logging.CRITICAL: COLOR_SEQ % MAGENTA
}

def format_heading(report, nestlevel, args):
    if args.color:
        fmtstring = '{BOLD}{indent}{datalevel} {index} {id}{RESET}'
    else:
        fmtstring = '{indent}{datalevel} {index} {id}'
    return fmtstring.format(
        BOLD=BOLD_SEQ,
        indent=' ' * nestlevel,
        datalevel=datalevels[nestlevel],
        index=str(report.get('index', '?')),
        id='' if not report.get('id') else '(id: "{}")'.format(report['id']),
        RESET=RESET_SEQ
    )

def format_message(record, nestlevel, args):
    if args.color:
        fmtstring = '{COLOR}{indent} * {message}{RESET}'
    else:
        fmtstring = '{indent} * {message}'
    return fmtstring.format(
            COLOR=COLORS[record['level']],
            indent=' ' * nestlevel,
            message=record['message'],
            RESET=RESET_SEQ
        )

# COMMANDLINE USE

def main(args):
    from xml.etree import ElementTree as ET
    for i, f in enumerate(args.files):
        with open(f, 'r') as fh:
            try:
                xc = xigtxml.load(fh, mode='transient')
            except ET.ParseError:
                print('Corpus {} ({}) failed to load. First verify '
                      'that the XML file is valid by doing a schema '
                      'validation.'
                      .format(i, f))
            else:
                report = filter_empty_reports(validate_corpus(xc))
                report['index'] = i
                print_report(report, args)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Validate Xigt documents.")
    add = parser.add_argument
    add('files', nargs='+')
    add('--color', action='store_true', help='Display results in color.')
    add('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='Increase the verbosity (can be repeated: -vvv).')
    add('-q', '--quiet',
        action='store_const', const=0, dest='verbosity',
        help='Set verbosity to the quietest level.')

    args = parser.parse_args()
    logging.basicConfig(
        level=50-(args.verbosity*10),
        format='%(message)s'
    )

    main(args)
