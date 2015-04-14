#!/usr/bin/env python3.2

# ODIN Importer
#
# default config.json:
# {
#   "input_file_suffix": ".txt",
#   "replacement_char": "�",
#   "clean": true,
#   "normalize": true,
#   "keep_headers": false,
# }
#
# input_file_suffix: when input is a directory, look for files with this suffix
# replacement_char: the character to use instead of invalid XML characters
# clean: if true, add a cleaned tier (type="odin" state="cleaned")
# normalize: if true, add a normalized tier (type="odin" state="normalized")
# keep_headers: put the ODIN header info in a <metadata> element on the igt
# used_igt_ids: don't reuse these IDs on <igt> elements

import sys
from os import mkdir
import os.path
import logging
import re
import unicodedata
import argparse
from collections import OrderedDict, defaultdict
from itertools import chain

from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta
from xigt.codecs import xigtxml
from xigt.errors import XigtImportError


def xigt_import(inpath, outpath, options=None):

    if options is None:
        options = {}
    options.setdefault('input_file_suffix', '.txt')
    options.setdefault('replacement_char', '\uFFFD')
    options.setdefault('clean', True)
    options.setdefault('normalize', True)
    options.setdefault('keep_headers', False)

    # other things to store in options
    options.setdefault('last_igt_id_number', 0)
    options['used_igt_ids'] = set()


    if os.path.isfile(inpath) and not os.path.isdir(outpath):
        _xigt_import(inpath, outpath, options)
    elif os.path.isdir(inpath) and not os.path.isfile(outpath):
        import glob
        suffix = options['input_file_suffix']
        if not os.path.exists(outpath):
            prepare_outdir(outpath)
        filepattern = '*{}'.format(suffix)
        for infile in glob.glob(os.path.join(inpath, filepattern)):
            outfile = re.sub(suffix + r'$', '.xml', os.path.basename(infile))
            _xigt_import(infile, os.path.join(outpath, outfile), options)
    else:
        raise XigtImportError(
            '--input and --output must both be files or both be directories'
        )


def _xigt_import(infile, outfile, options):
    with open(infile, 'r') as in_fh, open(outfile, 'w') as out_fh:
        igts = odin_igts(in_fh, options)
        xc = XigtCorpus(
            igts=igts,
            attributes={
                "xmlns:olac": "http://www.language-archives.org/OLAC/1.1/",
                "xmlns:dc": "http://purl.org/dc/elements/1.1/",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
            },
            mode='transient'
        )
        xigtxml.dump(out_fh, xc)


def prepare_outdir(outpath):
    try:
        mkdir(outpath)
    except OSError:
        raise XigtImportError(
            'Unable to create output directory: {}'
            .format(outpath)
        )


### PARSING IGTS #######################################################

def odin_igts(in_fh, options):
    last_igt_id_number = options['last_igt_id_number']
    for i, block in enumerate(odin_blocks(in_fh, options)):
        block['i'] = last_igt_id_number + i + 1
        igt = make_igt(block, options)
        if igt.get('r') is not None:
            if options['clean']:
                add_cleaned_tier(igt, options)
            if options['normalize']:
                add_normalized_tier(igt, options)
            yield igt
    options['last_igt_id_number'] = block['i']

def make_igt(block, options):

    igt_id = make_igt_id(block['i'], options['used_igt_ids'])
    options['used_igt_ids'].add(igt_id)

    attributes = make_igt_attributes(block, options)
    metadata = make_igt_metadata(block, options)
    raw_tier = make_igt_raw_tier(block, options)

    return Igt(
        id=igt_id,
        attributes=attributes,
        metadata=[metadata],
        tiers=[raw_tier]
    )

def make_igt_id(i, idset):
    new_id = 'igt{}'.format(i)
    ctr = 2
    while new_id in idset:
        new_id = 'igt{}_{}'.format(i, ctr)
        ctr += 1
    return new_id


def make_igt_attributes(block, options):
    return {
        'doc-id': block['doc_id'],
        'line-range': '-'.join(block['line_range']),
        'tag-types': ' '.join(block['line_types'])
    }


def make_igt_metadata(block, options):
    md = Metadata()
    mi = 1

    if options['keep_headers'] and block.get('header_lines'):
        md.append(Meta(id='meta{}'.format(mi),
                       type='odin-header',
                       text='\n'.join(block.get('header_lines', []))
        ))
        mi += 1

    lg_code = block.get('iso-639-3')
    if lg_code is None:
        lg_code = 'und'  # undetermined
    language = (block.get('language') or '').strip()

    subj = ('\n      <dc:subject xsi:type="olac:language" '
            'olac:code="{}">{}</dc:subject>'
            .format(lg_code.strip(), language))
    lang = ('\n      <dc:language xsi:type="olac:language" '
            'olac:code="en">English</dc:language>')
    md.append(Meta(id='meta{}'.format(mi), children=[subj, lang]))

    return md


def make_igt_raw_tier(block, options):
    items = [Item(id='r{}'.format(j+1), attributes=a, text=t)
             for j, (a, t) in enumerate(block.get('lines', []))]
    tier = Tier(
        id='r',
        type='odin',
        attributes={'state': 'raw'},
        items=items
    )
    return tier


def add_cleaned_tier(igt, options):
    raw_tier = igt['r']
    cleaned_items = clean_items(raw_tier.items)
    tier = Tier(
        id='c',
        type='odin',
        alignment=raw_tier.id,
        attributes={'state': 'cleaned'},
        items=cleaned_items
    )
    igt.append(tier)


def add_normalized_tier(igt, options):
    orig_tier = igt.get('c', default=igt['r'])
    norm_items = normalize_items(orig_tier.items)
    tier = Tier(
        id='n',
        type='odin',
        alignment=orig_tier.id,
        attributes={'state': 'normalized'},
        items=norm_items
    )
    igt.append(tier)


### READING ODIN TEXT ##################################################

doc_re = re.compile(r'doc_id=(?P<id>\S+) '
                    r'(?P<start>\d+) '
                    r'(?P<end>\d+) '
                    r'(?P<linetypes>.*)')


def odin_blocks(lines, options):
    line_iterator = iter(lines)
    for line in line_iterator:
        doc = doc_re.match(line)
        if doc is None:
            if 'doc_id=' in line:
                logging.warning('Possible ODIN instance missed: {}'
                                .format(line))
            continue

        header_lines = []
        lang = None
        iso639 = None
        odin_lines = []

        try:
            while line.strip() != '' and not line.startswith('line='):
                header_lines.append(line.rstrip())
                line = next(line_iterator)

            lang, iso639 = get_best_lang_match(header_lines)
            if lang is None or iso639 is None:
                logging.warning('Failed to get language or language code for '
                                'document {}, lines {}--{}.'
                                .format(doc.group('id'),
                                        doc.group('start'),
                                        doc.group('end')))
            else:
                logging.debug('Document {}, lines {}--{}, Language: {}, '
                              'ISO-639-3: {}'
                              .format(doc.group('id'),
                                      doc.group('start'),
                                      doc.group('end'),
                                      lang, iso639))

            while line.strip() != '':
                odin_lines.append(odin_line(line, options))
                line = next(line_iterator)

        except StopIteration:
            pass

        finally:
            yield {'doc_id': doc.group('id'),
                   'line_range': (doc.group('start'), doc.group('end')),
                   'line_types': doc.group('linetypes').split(),
                   'language': lang,
                   'iso-639-3': iso639,
                   'lines': odin_lines,
                   'header_lines': header_lines
                  }


lang_chosen_re = re.compile(r'(?P<name>.*) \((?P<iso639>[^)]+)\)\s*$',
                            re.UNICODE)
stage2_LN_re = re.compile(r'stage2_LN_lang_code: (?P<name>.*) '
                          r'\([^,]+, (?P<iso639>[^)]+)\)')
chosen_idx_re = re.compile(r'lang_chosen_idx=(?P<idx>[-0-9]+)')


def get_best_lang_match(lines):
    lang_lines = dict(l.split(':', 1) for l in lines if ':' in l)
    # find best match
    lang = iso639 = None
    if 'stage3_lang_chosen' in lang_lines:
        match = lang_chosen_re.search(lang_lines['stage3_lang_chosen'])
        if match:
            lang = match.group('name')
            iso639 = match.group('iso639')
    elif 'stage2_lang_chosen' in lang_lines:
        match = lang_chosen_re.search(lang_lines['stage2_lang_chosen'])
        if match:
            lang = match.group('name')
            iso639 = match.group('iso639')
    elif 'stage2_LN_lang_code' in lang_lines:
        first = lang_lines['stage2_LN_lang_code'].split('||', 1)[0]
        match = stage2LN_re.match(first)
        if match:
            lang = match.group('name')
            iso639 = match.group('iso639')
    elif 'lang_code' in lang_lines and \
         'lang_chosen_idx' in lang_lines['note']:
        match = chosen_idx_re.search(lang_lines['note'])
        if match:
            idx = int(match.group('idx'))
            if idx != -1:
                langstring = lang_lines['lang_code'].split('||')[idx]
                match = lang_chosen_re.match(langstring)
                if match:
                    lang = match.group('name')
                    iso639 = match.group('iso639')
    return lang, iso639


line_re = re.compile(r'line=(?P<line>\d+) tag=(?P<tag>[^:]+):(?P<content>.*)')


def odin_line(line, options):
    match = line_re.match(line)
    if match:
        attrs = OrderedDict([('line', match.group('line')),
                             ('tag', match.group('tag'))])
        line_content = replace_invalid_xml_chars(match.group('content'),
                                                 options['replacement_char'])
        return (attrs, line_content)
    else:
        logging.warning('Non-empty IGT line could not be parsed:\n{}'
                        .format(line))
        return ({}, '')


#Character replacement based on an answer by "drawnonward" on Stack Overflow
#http://stackoverflow.com/questions/3220031/how-to-filter-or-replace-unicode-characters-that-would-take-more-than-3-bytes

# XML 1.0 valid ranges:
#  \u0009, \u000A, \u000D, \u0020-\uD7FF, \uE000-\uFFFD, \U0001000-\U0010FFFF
# but these are discouraged:
#  \u007F-\u0084, \u0086-\u009F
# XML 1.1 valid ranges:
#  \u0001-\uD7FF, \uE000-\uFFFD, \U00010000-\U0010FFFF
# but these are discouraged:
#  \u0001-\u0008, \u000B-\u000C, \u000E-\u001F, \u007F-\u0084, \u0086-\u009F
# Moreover, these are allowed but are discouraged, and may be "invalid" by
# some parsers:
#  \uFDD0-\uFDDF
#  \U0001FFFE, \U0001FFFF, \U0002FFFE, \U0002FFFF, \U0003FFFE, \U0003FFFF,
#  \U0004FFFE, \U0004FFFF, \U0005FFFE, \U0005FFFF, \U0006FFFE, \U0006FFFF,
#  \U0007FFFE, \U0007FFFF, \U0008FFFE, \U0008FFFF, \U0009FFFE, \U0009FFFF,
#  \U000AFFFE, \U000AFFFF, \U000BFFFE, \U000BFFFF, \U000CFFFE, \U000CFFFF,
#  \U000DFFFE, \U000DFFFF, \U000EFFFE, \U000EFFFF, \U000FFFFE, \U000FFFFF,
#  \U0010FFFE, \U0010FFFF
invalid_char_re = re.compile('[^\x09\x0A\x0D\u0020-\uD7FF\uE000-\uFFFD'
                             #'\U00010000-\U0010FFFF]'
                             ']'
                             , re.UNICODE)


def replace_invalid_xml_chars(input, replacement_char):
    # \uFFFD is the unicode replacement character
    return invalid_char_re.sub(replacement_char, input)


### CLEANING ###########################################################

def copy_items(items):
    return [
        Item(id=item.id, type=item.type, alignment=item.alignment,
             content=item.content, segmentation=item.segmentation,
             attributes=item.attributes, text=item.text)
        for item in items
    ]


def clean_items(items):
    # first make copies of the original items
    cln_items = copy_items(items)
    # then execute the cleaning steps
    #cln_items = merge_diacritics(cln_items)
    cln_items = merge_lines(cln_items)

    for item in cln_items:
        item.alignment = item.id  # do this first so it aligns to rX
        item.id = item.id.replace('r', 'c')
    
    return cln_items


def merge_diacritics(items):
    """
    Use unicodedata's normalize function first to get combining
    diacritics instead of standalone ones, then for any combining
    diacritic see if it combines with a nearby character (where
    "combine" here means that the two can be normalized as a single
    character.
    """
    # this StackOverflow answer by bobince was very helpful:
    # http://stackoverflow.com/a/447047
    newitems = []
    for item in items:
        line = item.text
        if line.strip() == '':
            newitems.append(item)
            continue
        line = unicodedata.normalize('NFKD', line)
        # first remove inserted spaces before diacritics
        max_j = len(line) - 1
        line = ''.join(c for j, c in enumerate(line)
                       if c != ' ' or (j < max_j and
                                       unicodedata.combining(line[j+1])==0))
        # then combine diacritics with previous, then following chars if
        # they can be combined
        chars = [line[0]] # always append first char
        max_j = len(line) - 1 # need to recalc this
        for j, c in enumerate(line[1:]):
            # skipped first char, so counter needs to be incremented
            j += 1
            if unicodedata.combining(c):
                # a character x and combining character c have length 2,
                # but if they combine, they have length 1
                if j < max_j and \
                     len(unicodedata.normalize('NFC', line[j+1] + c)) == 1:
                    # just append
                    chars.append(unicodedata.normalize('NFC', line[j+1] + c))
                elif len(unicodedata.normalize('NFC', chars[-1] + c)) == 1:
                    # need to replace appended previous char
                    chars[-1] = unicodedata.normalize('NFC', chars[-1] + c)
            else:
                chars.append(c)
        # then check if combining diacritics match adjacent chars
        #for j, c in enumerate(line)
        item.text = ''.join(chars)
        newitems.append(item)
    return newitems


def merge_lines(items):
    """
    Return the lines with corrupted and split lines merged.
    Merge corrupted lines if:
      * Both lines have the +CR tag
      * Both lines have one other tag in common
      * The lines are sequential
      * tokens in one line align to whitespace in the other
    TODO:
      * Can we allow some non-whitespace overlap, in which case the
        token would be inserted in the closest match
      * Can we recombine diacritics with the letter it came from?
        E.g. is this usually accents or umlauts on vowels?
      * Is there anything that can be done about intraline corruption?
        E.g. when spaces are inserted w i t h i n words
    """
    n = len(items)
    # nothing to do if there's just 1 line
    if n < 2:
        return items
    newitems = [items[0]]
    for i in range(1,n):
        # lines are pairs of attributes and content
        prev = newitems[-1]
        cur = items[i]
        p_tags = prev.attributes.get('tag','').split('+')
        c_tags = cur.attributes.get('tag','').split('+')
        # if no non-CR tags are shared
        if 'CR' not in c_tags or \
           len(set(p_tags).intersection(c_tags).difference(['CR'])) == 0:
            newitems.append(cur)
            continue
        merged = bit_merge(prev.text, cur.text)
        if merged is not None:
            # there's no OrderedSet, but OrderedDict will do
            tags = OrderedDict((t,1) for t in p_tags + c_tags)
            line_nums = ' '.join([prev.attributes.get('line'),
                                  cur.attributes.get('line')])
            prev.attributes['tag'] = '+'.join(tags)
            prev.attributes['line'] = line_nums
            prev.text = merged
    return newitems


def merge_strings(a, b):
    maxlen = max([len(a), len(b)])
    a = a.ljust(maxlen)
    b = b.ljust(maxlen)
    m = []
    for i in range(maxlen):
        pass
        # do something like this
        #   "a a a"  "a a a"    "a a a"  "a a a"  "a a a"
        # + " b"     " bbb "    " b b "  "  b"    "  bb"
        # = "aba a"  "abbba a"  "ababa"  "a aba"  "a abba"

    return ''.join(m).rstrip(' ')


def bit_merge(a, b):
    """
    Merge two strings on whitespace by converting whitespace to the
    null character, then AND'ing the bit strings of a and b, then
    convert back to regular strings (with spaces).
    """
    if len(b) > len(a): return bit_merge(b, a)
    try:
        # get bit vectors with nulls instead of spaces, and
        # make sure the strings are the same length
        a = a.replace(' ','\0').encode('utf-8')
        b = b.replace(' ','\0').encode('utf-8').ljust(len(a), b'\0')
        c_pairs = zip(a, b)
    except UnicodeDecodeError:
        return None
    c = []
    for c1, c2 in c_pairs:
        # only merge if they merge cleanly
        if c1 != 0 and c2 != 0:
            return None
        else:
            c.append(c1|c2)
    try:
        return bytes(c).decode('utf-8').replace('\0',' ').rstrip(' ')
    except UnicodeDecodeError:
        return None


### NORMALIZING ########################################################

def normalize_items(items):
    # first make copies of the original items
    nrm_items = copy_items(items)

    # and set the copy's alignments to their current ID (changed later)
    for item in nrm_items:
        item.alignment = item.id

    # nrm_items = rejoin_lines(nrm_items)
    nrm_items = list(map(normalize_line, nrm_items))

    for i, item in enumerate(nrm_items):
        item.id = 'n{}'.format(i+1)

    return nrm_items


paren_re = re.compile(r'\([^)]*\)')
paren_num_re = re.compile(
    r"^\(\s*(" # start (X; ( X; group for alternates
    r"[\d.]+\w?|\w|" # 1 1a 1.a 1.23.4b; a b (no multiple chars, except...)
    r"[ivxlc]+)"    # roman numerals: i iv xxiii; end alt group
    r"['.:]*\s*\)[.:]*") # optional punc (X) (X:) (X') (X.) (X. ) (X). (X):
num_re = re.compile(
    r"^([\d.]+\w?|\w|[ivxlc]+)" # nums w/no parens; same as above
    r"['.):]+\s" # necessary punc; 1. 1' 1) 1: 10.1a. iv: etc.
)
precontent_re = re.compile(r'^\s*\w+(\s\w+)?\s*:\s')
hyphen_re = re.compile(r'\s*-\s*')


def normalize_line(item):
    line = item.text
    if line is None or line.strip() == '': return item
    # remove spaces, quotes, and punctuation to make later regexes simpler
    line = line.strip().strip('"\'`')
    # only strip initial parens if on both sides (so we don't turn 'abc (def)'
    # into 'abc (def'
    if line.startswith('(') and line.endswith(')'): line = line[1:-1]
    # one more space, quote, and punc strip, in case the parens grouped them
    line = line.strip().strip('"\'`')
    # re-add a period (to all lines)
    # remove inner parens (with encapsulated content)
    # this seems to to go too far in some cases, see ace.item11
    #line = paren_re.sub('', line)
    # IGT-initial numbers (e.g. '1.' '(1)', '5a.', '(ii)')
    line = paren_num_re.sub('', line).strip()
    line = num_re.sub('', line).strip()
    # precontent tags can be 1 or 2 words ("intended:" or "speaker", "a:")
    # ignore those with 3 or more
    line = precontent_re.sub('', line)
    # there may be morphemes separated by hyphens, but with intervening
    # spaces; remove those spaces (e.g. "dog-  NOM" => "dog-NOM")
    line = hyphen_re.sub('-', line)
    # ignore ungrammatical or questionably lines or those with alternates
    # now we want to include these, separate out the # or * and mark the
    # judgments  for /, it's no longer a bother
    # do this later anyway
    # if line.startswith('*') or line.startswith('#'): or '/' in line:
    #    return None
    
    item.text = line
    return item
