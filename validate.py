#!/usr/bin/env python3

from collections import Counter
import logging
import warnings
warnings.simplefilter('ignore')

from xigt.codecs import xigtxml
from xigt.core import (
    get_alignment_expression_ids as get_ae_ids,
    XigtAttributeError
)

datalevels = ['corpus', 'igt', 'tier', 'item']
reference_attributes = ['alignment', 'segmentation', 'content']


# VALIDATORS

def make_context(obj, index, name, scope, **kwargs):
    context = {
        'id': getattr(obj, 'id', None),
        'index': index,
        'name': name,
        'scope': scope
    }
    for k, v in kwargs.items():
        context[k] = v
    return context

def validate_condition(condition, obj, context):
    records = []
    make_record, cond, *args = condition
    results = cond(obj, *args)
    if results:
        if isinstance(results, str):
            results = [results]
        for result in results:
            msg = result.format(modal=make_record.__doc__, **context)
            records.append(make_record(msg))
    return records


def validate(obj, context, conditions):
    records = []
    children = []
    for condition in conditions:
        records.extend(validate_condition(condition, obj, context))
    report = {'records': records, 'children': children,
              'id': obj.id, 'index': context.get('index')}
    return report

def validate_corpus(xc, context):
    report = validate(
        xc,
        context=context,
        conditions=[
            # todo validate_metadata here
            (may, has_id),
            (must, id_is_unique, context.get('ids', []))
        ]
    )
    igt_ids = Counter()
    for i, igt in enumerate(xc):
        igtcontext = make_context(igt, i, '<igt>', '<xigt-corpus>')
        igtreport = validate_igt(igt, igtcontext)

        # corpus-level constraints on sub-items go here, such as ID uniqueness
        # check for igt id uniqueness in the <xigt-corpus>
        igtreport['records'].extend(
            validate_condition((must, id_is_unique, igt_ids), igt, igtcontext)
        )
        add_id(igt_ids, igt)

        # all done; append the report
        report['children'].append(igtreport)

    return report


def validate_igt(igt, context):
    report = validate(
        igt,
        context=context,
        conditions=[
            (should, has_id),
        ]
    )

    tier_ids = Counter()
    item_ids = Counter()
    for i, tier in enumerate(igt):
        tierctxt = make_context(tier, i, '<tier>', '<igt>')
        tierreport = validate_tier(tier, tierctxt)

        # igt-level constraints on sub-items go here, such as ID uniqueness
        # check for tier id uniqueness in the <igt>
        tierreport['records'].extend(
            validate_condition((must, id_is_unique, tier_ids), tier, tierctxt)
        )
        add_id(tier_ids, tier)

        # check for item id uniqueness in the <igt>
        for j, pair in enumerate(zip(tier.items, tierreport['children'])):
            item, itemreport = pair
            itemctxt = make_context(item, j, '<item>', '<igt>')
            itemreport['records'].extend(
                validate_condition((must, id_is_unique, item_ids),
                                   item, itemctxt)
            )
            add_id(item_ids, item)

        # all done; append the report
        report['children'].append(tierreport)

    return report

def validate_tier(tier, context):
    conditions = [
        (should, has_id),
        (should, has_type)
    ]
    for refattr in reference_attributes:
        conditions.append((must, refattr_in_igt, refattr))

    report = validate(tier, context=context, conditions=conditions)

    # validate tier metadata

    item_ids = Counter()
    for i, item in enumerate(tier):
        itemctxt = make_context(item, i, '<item>', '<tier>')
        itemreport = validate_item(item, itemctxt)

        # tier-level constraints on sub-items go here, such as ID uniqueness
        # check for item id uniqueness in the <tier>
        itemreport['records'].extend(
            validate_condition((must, id_is_unique, item_ids), item, itemctxt)
        )
        add_id(item_ids, item)

        # all done; append the report
        report['children'].append(itemreport)

    return report


def validate_item(item, context):
    conditions = [
        (should, has_id),
    ]
    for refattr in reference_attributes:
        conditions.append((must, refattr_in_aligned_tier, refattr))
    report = validate(
        item,
        context=context,
        conditions=conditions
    )
    return report


# TEST HELPERS

def must(msg):
    "MUST"
    return {'level': logging.ERROR, 'message': msg}

def should(msg):
    "SHOULD"
    return {'level': logging.WARNING, 'message': msg}

def may(msg):
    "MAY"
    return {'level': logging.INFO, 'message': msg}

def add_id(ids, obj):
    if getattr(obj, 'id', None) is not None:
        ids[obj.id] += 1

# TEST FUNCTIONS

## Each function should return a result if the test failed. The result
## may be a string or a list of strings (in case of multiple errors).
## An empty string or other False value (including None) is taken to
## mean the test has passed. Each result string can use the following
## substitutions:
##   {index} : the index of the object in its list
##   {id}    : the id of the object (may be None)
##   {name}  : the name of the element, such as <igt>, <tier>, or <item>
##   {modal} : "MUST", "SHOULD", "MAY"
##   {scope} : the level at which the test failed (e.g. <igt>, <tier>, etc.)
## In general, {index} and {id} are not needed because that information is
## available in the report structure (report['index'] and report['id'])

def has_id(obj):
    if not bool(getattr(obj, 'id', None)):
        return "Each {name} {modal} specify an id."

def id_is_unique(obj, idset):
    if bool(getattr(obj, 'id', None)) and obj.id in idset:
        return "The given id for each {name} {modal} be unique within its {scope}."

def has_type(obj):
    if not bool(getattr(obj, 'type', None)):
        return "Each {name} {modal} specify a type."

def refattr_in_igt(tier, refattr):
    refid = tier.attributes.get(refattr)
    if refid and tier.igt.get(refid) is None:
        return ('The reference attribute "{}" {{modal}} select an '
                'available <tier> id.'.format(refattr))

def refattr_in_aligned_tier(item, refattr):
    itemref = item.attributes.get(refattr)
    tierref = item.tier.attributes.get(refattr)
    if not itemref or not tierref:
        return
    reftier = item.igt.get(tierref)
    if not reftier:
        return
    missing = []
    for ae_id in get_ae_ids(itemref):
        if reftier.get(ae_id) is None:
            missing.append(ae_id)
    if missing:
        return (
            'The alignment expression "{}" {{modal}} select available '
            '<item> ids from the aligned <tier> ("{}"). The following are '
            'unavailable: {}'.format(refattr, tierref, ', '.join(missing))
        )


def test_overlapping_ae(item, report):
    for ref in reference_attributes:
        if ref not in item.attributes:
            continue


# FILTERING

def report_is_empty(report, minlevel=None):
    return not any([rec for rec in report.get('records', [])
                    if minlevel is None or rec['level'] >= minlevel]
                   + report.get('children', []))

def filter_empty_reports(report, minlevel=None):
    report['children'] = [filter_empty_reports(child, minlevel)
                          for child in report.get('children', [])]
    if report_is_empty(report, minlevel):
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
    passed = []
    from xml.etree import ElementTree as ET
    ids = Counter()
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
                context = make_context(
                    xc, i, '<xigt-corpus>', 'collection', ids=ids
                )
                report = validate_corpus(xc, context)
                report = filter_empty_reports(
                    report, minlevel=logging.getLogger().getEffectiveLevel()
                )
                if report_is_empty(report):
                    passed.append(True)
                else:
                    passed.append(False)
                    print_report(report, args)
                add_id(ids, xc)
    return all(passed)

if __name__ == '__main__':
    import argparse
    import sys

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
        level=60-(args.verbosity*10),
        format='%(message)s'
    )

    success = main(args)
    sys.exit(0 if success else 1)
