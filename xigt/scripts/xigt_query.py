#!/usr/bin/env python3

from __future__ import print_function
import argparse
from collections import defaultdict
from xigt import XigtCorpus, Igt
from xigt.codecs import xigtxml


def print_stats(args):
    def new_stats():
        return {
            'languages': set(),
            'iso-639-3': defaultdict(lambda: defaultdict(int)),
            'instances': 0,
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
                stats['instances'] += 1
                cur_stats['instances'] += 1
                # language is in a meta element
                lgs = igt.get_meta('language', conditions=[lg_condition])
                if lgs:
                    lg_name = lgs[0].attributes.get('name', '???').strip()
                    lg_iso = lgs[0].attributes.get('iso-639-3', '???').strip()
                else:
                    lg_name = ''
                    lg_iso = ''
                stats['languages'].add(lg_name.lower())
                cur_stats['languages'].add(lg_name.lower())
                stats['iso-639-3'][lg_iso][lg_name] += 1
                cur_stats['iso-639-3'][lg_iso][lg_name] += 1
                # count tiers and items by types, IGTs by tier types
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

        if args.summarize_each:
            print_summary('{} summary:'.format(f), cur_stats)
        if args.languages_each:
            print_languages('Languages used in {}:'.format(f),
                            cur_stats['iso-639-3'])
    if args.summarize:
        print_summary('Overall summary ({} file{}):'
                      .format(num_files, 's' if num_files != 1 else ''),
                      stats)
    if args.languages:
        print_languages('Languages used overall ({} file{}):'
                        .format(num_files, 's' if num_files != 1 else ''),
                        stats['iso-639-3'])


def print_summary(title, stats):
    print(title)
    st = stats
    maxlen = max(
        map(lambda x: len(str(x)),
            [len(st['languages']), len(st['iso-639-3']), st['instances']] +
            list(st['igts'].values()) +
            list(st['tiers'].values()) +
            list(st['items'].values()))
    )
    template = ' {{:>{}}} {{}}'.format(maxlen)
    print(template.format(st['instances'], 'IGT instances'))
    print(template.format(len(st['languages']), 'languages (by name)'))
    print(template.format(len(st['iso-639-3']),
                          'languages (by ISO-639-3 language code)'))
    for igt_type in st['igts']:
        print(template.format(st['igts'][igt_type],
                              'IGTs with tiers: {}'.format(
                                  ', '.join(igt_type))))
    for tier_type in st['tiers']:
        print(template.format(st['tiers'][tier_type],
                              'tiers of type: {}'.format(tier_type)))
    for item_type in st['items']:
        print(template.format(st['items'][item_type],
                              'items of type: {}'.format(
                                  item_type or '(None)')))
    print()  # just always put a blank line at the end


def print_languages(title, lg_stats):
    lgs = sorted(((code, name, count)
                  for code in lg_stats
                  for name, count in lg_stats[code].items()),
                 key=lambda x: (-x[2], x[1]))
    print(title)
    for code, name, count in lgs:
        print('  {}\t{}\t{}'.format(code, name, count))
    print()


def main(arglist=None):
    parser = argparse.ArgumentParser(
        description='Query Xigt documents.'
    )
    parser.add_argument(
        '-S', '--summarize', action='store_true',
        help='Produce a summary of all input files.')
    parser.add_argument(
        '-s', '--summarize-each', action='store_true',
        help='Produce a summary for each input file.')
    parser.add_argument(
        '-L', '--languages', action='store_true',
        help='List the languages used in the input files with their counts.')
    parser.add_argument(
        '-l', '--languages-each', action='store_true',
        help='List the languages used in each input file with their counts.')
    #parser.add_argument('-m' '--xigt-meta')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(arglist)

    if args.summarize or args.summarize_each or \
       args.languages or args.languages_each:
        print_stats(args)


if __name__ == '__main__':
    main()