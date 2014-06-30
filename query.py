#!/usr/bin/env python3

import argparse
from collections import defaultdict
from xigt import XigtCorpus, Igt
from xigt.codecs import xigtxml


def summary(args):
    def new_stats():
        return {
            'languages': set(),
            'iso-639-3': set(),
            'documents': 0,
            'igts': defaultdict(int),
            'tiers': defaultdict(int),
            'items': defaultdict(int),
        }
    stats = new_stats()
    lg_condition = lambda m: 'phrases' in m.attributes.get('tiers', '')
    num_files = 0
    for f in args.files:
        with open(f, 'r') as fh:
            num_files += 1
            cur_stats = new_stats()
            xc = xigtxml.load(fh, mode='transient')
            for igt in xc:
                stats['documents'] += 1
                cur_stats['documents'] += 1
                # language is in a meta element
                lgs = igt.get_meta('language', conditions=[lg_condition])
                if lgs:
                    lg_name = lgs[0].attributes.get('name', '').strip().lower()
                    lg_iso = lgs[0].attributes.get('iso-639-3')
                stats['languages'].add(lg_name)
                cur_stats['languages'].add(lg_name)
                stats['iso-639-3'].add(lg_iso)
                cur_stats['iso-639-3'].add(lg_iso)
                #
                all_tier_types = set()
                for tier in igt:
                    stats['tiers'][tier.type] += 1
                    cur_stats['tiers'][tier.type] += 1
                    all_tier_types.add(tier.type)
                    for item in tier:
                        stats['items'][item.type] += 1
                        cur_stats['items'][item.type] += 1
                stats['igts'][tuple(sorted(all_tier_types))] += 1
                cur_stats['igts'][tuple(sorted(all_tier_types))] += 1

        if args.summzarize_each:
            print_summary(f, cur_stats)
    print_summary('Overall ({} file{})'
                  .format(num_files, 's' if num_files != 1 else ''),
                  stats)


def print_summary(title, stats):
    print(title)
    st = stats
    maxlen = max(
        map(lambda x: len(str(x)),
            [len(st['languages']), len(st['iso-639-3']), st['documents']] +
            list(st['igts'].values()) +
            list(st['tiers'].values()) +
            list(st['items'].values()))
    )
    template = '{{:>{}}} {{}}'.format(maxlen + 1)
    print(template.format(st['documents'], 'source documents'))
    print(template.format(len(st['languages']), 'languages (by name)'))
    print(template.format(len(st['iso-639-3']),
                          'languages (by ISO-639-3 language code)'))
    for igt_type in st['igts']:
        print(template.format(st['igts'][igt_type],
                              'IGTs with tiers {}'.format(str(igt_type))))
    for tier_type in st['tiers']:
        print(template.format(st['tiers'][tier_type],
                              'tiers of type {}'.format(str(tier_type))))
    for item_type in st['items']:
        print(template.format(st['items'][item_type],
                              'items of type {}'.format(str(item_type))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Query Xigt documents.'
    )
    parser.add_argument(
        '-S', '--summarize', action='store_true',
        help='Produce a summary of all input files.')
    parser.add_argument(
        '-s', '--summzarize-each', action='store_true',
        help='Produce a summary for each input file.')
    parser.add_argument('-l', '--languages', action='store_true')
    parser.add_argument('-m' '--xigt-meta')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    if args.summarize:
        summary(args)
