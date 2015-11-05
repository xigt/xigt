#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-

# ODIN Importer
#
# default config.json:
# {
#   "input_file_suffix": ".txt",
#   "replacement_char": "�",
#   "keep_headers": false
# }
#
# input_file_suffix: when input is a directory, look for files with this suffix
# replacement_char: the character to use instead of invalid XML characters
# keep_headers: put the ODIN header info in a <metadata> element on the igt
#
# 2015-10-30: removing the following:
#   "clean": true,
#   "normalize": true,
#
# clean: if true, add a cleaned tier (type="odin" state="cleaned")
# normalize: if true, add a normalized tier (type="odin" state="normalized")
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

import odintxt # https://github.com/xigt/odin-utils

from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
from xigt.codecs import xigtxml
from xigt.errors import XigtImportError

_nsmap={
    "olac": "http://www.language-archives.org/OLAC/1.1/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

def xigt_import(inpath, outpath, options=None):

    if options is None:
        options = {}
    options.setdefault('input_file_suffix', '.txt')
    options.setdefault('replacement_char', '\uFFFD')
    # options.setdefault('clean', True)
    # options.setdefault('normalize', True)
    options.setdefault('keep_headers', False)

    # other things to store in options
    # options.setdefault('last_igt_id_number', 0)
    # options['used_igt_ids'] = set()

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
            nsmap=_nsmap,
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
    for block in odintxt.odin_blocks(in_fh):
        igt = make_igt(block, options)
        if igt.get('r') is not None:
            yield igt


def make_igt(block, options):
    igt_id = block.get('igt_id', None)

    attributes = make_igt_attributes(block, options)
    metadata = make_igt_metadata(block, options)
    raw_tier = make_igt_raw_tier(block, options)

    return Igt(
        id=igt_id,
        attributes=attributes,
        metadata=[metadata],
        tiers=[raw_tier]
    )


def make_igt_attributes(block, options):
    start, end = block['line_range'].split()
    return {
        'doc-id': block['doc_id'],
        'line-range': '-'.join([start, end]),
        'tag-types': block['line_types']
    }


def qattrname(attrname, namespace=None):
    if namespace in _nsmap:
        return '{%s}%s' % (_nsmap[namespace], attrname)
    elif namespace is not None:
        raise XigtImportError(
            'Unspecified namespace prefix: {}'.format(namespace)
        )
    else:
        return attrname


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
    # should we title-case language?
    # language = (block.get('language') or '').strip().title()
    language = (block.get('language') or '').strip()

    subj = MetaChild(
        'subject',
        attributes={
            qattrname('type', 'xsi'): 'olac:language',
            qattrname('code', 'olac'): lg_code.strip()
        },
        text=language.title(),
        namespace=_nsmap['dc']
    )
    lang = MetaChild(
        'language',
        attributes={
            qattrname('type', 'xsi'): 'olac:language',
            qattrname('code', 'olac'): 'en'
        },
        text='English',
        namespace=_nsmap['dc']
    )
    md.append(Meta(id='meta{}'.format(mi), children=[subj, lang]))

    return md


def make_igt_raw_tier(block, options):
    items = []
    for j, linedata in enumerate(block.get('lines', [])):
        text = replace_invalid_xml_chars(
            linedata.get('content', ''),
            options['replacement_char']
        )
        attrs = linedata.copy()
        del attrs['content']
        items.append(Item(id='r{}'.format(j+1), attributes=attrs, text=text))
    tier = Tier(
        id='r',
        type='odin',
        attributes={'state': 'raw'},
        items=items
    )
    return tier


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
