#!/usr/bin/env python

from __future__ import print_function
import argparse
from collections import Counter, defaultdict
import string
import logging

from xigt import XigtCorpus, Igt, xigtpath as xp
from xigt.codecs import xigtxml


# see here: http://stackoverflow.com/a/34033230/1441112
class SafeFormatter(string.Formatter):
    def vformat(self, format_string, args, kwargs):
        args_len = len(args)  # for checking IndexError
        tokens = []
        for (lit, name, spec, conv) in self.parse(format_string):
            # re-escape braces that parse() unescaped
            lit = lit.replace('{', '{{').replace('}', '}}')
            # only lit is non-None at the end of the string
            if name is None:
                tokens.append(lit)
            else:
                # but conv and spec are None if unused
                conv = '!' + conv if conv else ''
                spec = ':' + spec if spec else ''
                # name includes indexing ([blah]) and attributes (.blah)
                # so get just the first part
                fp = name.split('[')[0].split('.')[0]
                # treat as normal if fp is empty (an implicit
                # positional arg), a digit (an explicit positional
                # arg) or if it is in kwargs
                if not fp or fp.isdigit() or fp in kwargs:
                    tokens.extend([lit, '{', name, conv, spec, '}'])
                # otherwise escape the braces
                else:
                    tokens.extend([lit, '{{', name, conv, spec, '}}'])
        format_string = ''.join(tokens)  # put the string back together
        # finally call the default formatter
        return string.Formatter.vformat(self, format_string, args, kwargs)

safe_format = SafeFormatter().format


# Just so {match!s} prints a simple comma-separated list
class CSTuple(tuple):
    def __str__(self):
        return ', '.join(map(str, self))


def run(args):
    job = make_job(args)
    agenda = job['agenda']
    global_c = defaultdict
    for infile in args.infiles:
        print(job['file_description'].format(filename=infile))
        xc = xigtxml.load(infile)
        results = process_agenda(xc, agenda)
        print_results(results)
        print()

def make_job(args):
    job = {"agenda": []}  # load from json file?
    if args.file_description:
        job['file_description'] = args.file_description
    elif not job.get('file_description'):
        job['file_description'] = '{filename}:'

    agenda = job['agenda']
    for action, vals in args.agenda:
        if action == 'description' and agenda:
            agendum = agenda[-1]
            agendum['description'] = safe_format(
                vals, query=agendum['query'], subquery=agendum.get('subquery')
            )
        else:
            if action in ('find', 'unique'):
                query, subquery = vals[0], ''
                description = '{query}\t{match!s}'
            elif action == 'tally':
                query, subquery = vals
                description = '{query}\t{subquery}\t{match!s}'
            agenda.append({
                'action': action,
                'query': query,
                'subquery': subquery,
                'description': safe_format(
                    description, query=query, subquery=subquery
                )
            })
    return job


def process_agenda(xc, agenda):
    results = []
    for agendum in agenda:
        agendum['result'] = None
        action = agendum['action']
        if action == 'find':
            find_pattern(xc, agendum)
        elif action == 'tally':
            results.extend(tally_pattern(xc, agendum))
        elif action == 'unique':
            results.append(unique_pattern(xc, agendum))
    return results


def find_pattern(xc, agendum):
    for match in xp.findall(xc, agendum['query']):
        print(' ', agendum['description'].format(match=match))


def tally_pattern(xc, agendum):
    counts = Counter()
    for match in xp.findall(xc, agendum['query']):
        group = CSTuple(xp.findall(match, agendum['subquery']))
        counts[group] += 1
    return [
        (count, agendum['description'].format(match=match))
        for match, count in counts.most_common()
    ]


def unique_pattern(xc, agendum):
    counts = Counter(xp.findall(xc, agendum['query']))
    return (len(counts), agendum['description'].format(match=''))


def print_results(results):
    if results:
        max_len = max(len(str(cnt)) for cnt, _ in results)
        for cnt, desc in results:
            print(' {}\t{}'.format(str(cnt).rjust(max_len), desc))

class AgendaAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if 'agenda' not in namespace:
            namespace.agenda = []
        namespace.agenda.append((self.dest, values))


def main(arglist=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Query Xigt documents.',
        epilog='examples:\n'
            '    xigt query --find \'igt/tier[@type="words"]/item/value()\' x.xml\n'
            '    xigt query --tally \'igt\' \'.//item[value()="dog"]\'\n'
            '               --description "IGTs with \'dog\' tokens" x.xml'
    )
    parser.add_argument('-v', '--verbose',
        action='count', dest='verbosity', default=2,
        help='increase the verbosity (can be repeated: -vvv)'
    )
    parser.add_argument('infiles', nargs='+')
    parser.add_argument('-f', '--find',
        nargs=1, metavar='QUERY', action=AgendaAction,
        help='find matches for XigtPath XP'
    )
    parser.add_argument('-t', '--tally',
        nargs=2, metavar=('QUERY', 'SUBQUERY'), action=AgendaAction,
        help='count results of QUERY grouped by results of SUBQUERY'
    )
    parser.add_argument('-u', '--unique',
        nargs=1, metavar='QUERY', action=AgendaAction,
        help='count unique matches of QUERY'
    )
    parser.add_argument('-d', '--description',
        metavar='DESC', action=AgendaAction,
        help='description for each result (can use {query}, {subquery} '
             'and {match})'
    )
    parser.add_argument('-D', '--file-description',
        metavar='DESC',
        help='description header for each file (can use {filename})'
    )
    args = parser.parse_args(arglist)
    agenda = getattr(args, 'agenda', [])
    if agenda and agenda[0][0] == 'description':
        parser.error('--description must follow an action (e.g., --tally)')
    logging.basicConfig(level=50-(args.verbosity*10))
    run(args)

if __name__ == '__main__':
    main()
