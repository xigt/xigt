#!/usr/bin/env python3

# Toolbox Importer
#
# default config.json:
# {
#   "record_markers": [
#     "\\id",
#     "\\ref"
#   ],
#   "igt_attribute_map": {
#     "\\id": "corpus-id"
#   },
#   "tier_map": {
#     "\\t": "w",
#     "\\m": "m",
#     "\\g": "g",
#     "\\p": "pos",
#     "\\f": "t"
#   },
#   "make_phrase_tier": ["w", "p"],
#   "tier_types": {
#     "p": {"type": "phrases"},
#     "w": {"type": "words", "interlinear": true},
#     "m": {"type": "morphemes", "interlinear": true},
#     "g": {"type": "glosses", "interlinear": true},
#     "pos": {"type": "pos", "interlinear": true},
#     "t": {"type": "translations"}
#   },
#   "alignments": {
#     "w": ["segmentation", "p"],
#     "m": ["segmentation", "w"],
#     "g": ["alignment", "m"],
#     "pos": ["alignment", "m"],
#     "t": ["alignment", "p"]
#   },
#   "error_recovery_method": "ratio"
# }

from __future__ import absolute_import

import io
from collections import OrderedDict
import logging
import warnings
try:
    from itertools import chain, zip_longest
except ImportError:
    from itertools import chain, izip_longest as zip_longest

from xigt import (XigtCorpus, Igt, Tier, Item, Metadata, Meta)
from xigt.codecs import xigtxml
from xigt.errors import XigtImportError

try:
    import toolbox
except ImportError:
    raise ImportError(
        'Could not import Toolbox module. Get it from here:\n'
        '  https://github.com/goodmami/toolbox'
    )

default_record_markers = [
    '\\id',
    '\\ref'
]

default_igt_attribute_map = {
    '\\id': 'corpus-id'
}

default_tier_map = {
    "\\t": "w",
    "\\m": "m",
    "\\g": "g",
    "\\p": "pos",
    "\\f": "t"
}

# if set, join tokens from first id to make phrase tier with second id
default_make_phrase_tier = ["w", "p"]

default_tier_types = {
    "p": {"type": "phrases"},
    "w": {"type": "words", "interlinear": True},
    "m": {"type": "morphemes", "interlinear": True},
    "g": {"type": "glosses", "interlinear": True},
    "pos": {"type": "pos", "interlinear": True},
    "t": {"type": "translations"}
}

# align Xigt tier IDs, not Toolbox markers
default_alignments = {
    "w": ["segmentation", "p"],
    "m": ["segmentation", "w"],
    "g": ["alignment", "m"],
    "pos": ["alignment", "m"],
    "t": ["alignment", "p"]
}

default_error_recovery_method = 'ratio'


def xigt_import(infile, outfile, options=None, encoding=None):

    if options is None:
        options = {}
    options.setdefault('record_markers', default_record_markers)
    options.setdefault('igt_attribute_map', default_igt_attribute_map)
    options.setdefault('tier_map', default_tier_map)
    options.setdefault('make_phrase_tier', default_make_phrase_tier)
    options.setdefault('tier_types', default_tier_types)
    options.setdefault('alignments', default_alignments)
    options.setdefault('error_recovery_method', default_error_recovery_method)

    # just use existing info to create marker-based alignment info
    options['tb_alignments'] = _make_tb_alignments(options) 

    with io.open(infile, 'r', encoding=encoding) as in_fh, \
         open(outfile, 'w') as out_fh:
        tb = toolbox.read_toolbox_file(in_fh)
        igts = toolbox_igts(tb, options)
        xc = XigtCorpus(igts=igts, mode='transient')
        xigtxml.dump(out_fh, xc)


def _make_tb_alignments(opts):
    inv_tier_map = {t: m for m, t in opts['tier_map'].items()}
    interlinear = {t: d.get('interlinear', False)
                   for t, d in opts['tier_types'].items()}
    tb_alignments = {}
    for t1, aln in opts['alignments'].items():
        refattr, t2 = aln
        if interlinear.get(t1, False) and interlinear.get(t2, False):
            tb_alignments[inv_tier_map[t1]] = inv_tier_map[t2]
    return tb_alignments


def toolbox_igts(tb, options):
    corpus_opts = options.get('xigt-corpus', {})
    record_markers = options['record_markers']
    assert len(record_markers) > 0
    mkrPriKey = record_markers[-1]
    for context, data in toolbox.records(tb, record_markers):
        data = list(data)  # run the generator
        if context.get(mkrPriKey) is None:
            continue  # header info
        igt = make_igt(
            context[mkrPriKey], data, context, options
        )
        if igt is not None:
            yield igt

def make_igt(key, data, context, options):
    # IDs must start with a letter
    assert key
    if not key[0].isalpha():
        key = 'igt{}'.format(key)
    if context is None:
        context = {}
    attrs = {}
    attmap = options['igt_attribute_map']
    for (mkr, val) in chain(data, context.items()):
        if val is None:  # will be None if mkr not encountered
            continue
        if mkr in attmap:
            attrs[attmap[mkr]] = val
    metadata = None

    w = None
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')

        try:
            tiers = make_all_tiers(data, options)
            igt = Igt(
                id=key,
                attributes=attrs,
                metadata=metadata,
                tiers=tiers
            )
        except (toolbox.ToolboxError, XigtImportError) as ex:
            logging.error('Error during import of item {}:\n  {}'
                          .format(key, str(ex)))
            igt = None
        if len(ws) > 0:
            w = ws[0]

    if w is not None:
        if issubclass(w.category, toolbox.ToolboxWarning):
            warnings.warn('{}: {}'.format(key, w.message), w.category)
        else:
            warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)

    return igt


def make_all_tiers(item_data, options):
    tier_map = options['tier_map']
    tier_types = options['tier_types']
    alignments = options['alignments']
    tb_alignments = options['tb_alignments']
    phrase_opts = options.get('make_phrase_tier')
    aligned_tiers = set(tb_alignments.keys()).union(tb_alignments.values())
    # use strip=False because we want same-length strings
    tier_data = toolbox.normalize_record(item_data, aligned_tiers, strip=False)
    prev = {}
    aligned_fields = toolbox.align_fields(
        tier_data, tb_alignments, errors=options['error_recovery_method']
    )
    for mkr, aln_tokens in aligned_fields:
        if mkr not in tier_map:
            continue
        tier_id = tier_map.get(mkr)
        if phrase_opts and phrase_opts[0] == tier_id:
            tier = make_phrase_tier(phrase_opts[1], aln_tokens)
            prev[phrase_opts[1]] = tier
            yield tier
        tier_type = tier_types[tier_id].get('type')
        refattr, aln_id = alignments.get(tier_id, (None, None))
        algn_tier = prev.get(aln_id)  # could be None
        try:
            tier = make_tier(tier_type, tier_id,
                             refattr, aln_tokens, algn_tier)
        except (AttributeError, AssertionError):
            raise XigtImportError('Error making {} tier (marker: {}).'
                                  .format(tier_type, mkr))
        prev[tier_id] = tier
        yield tier


def make_phrase_tier(tier_id, aln_tokens):
    return Tier(
        id=tier_id,
        type='phrases',
        items=[
            Item(
                id='{}1'.format(tier_id),
                text=' '.join(t for aln in aln_tokens for t in (aln[1] or []))
            )
        ]
    )


def make_tier(tier_type, tier_id, refattr, aln_tokens, algn_tier):
    attrs = OrderedDict()
    items = list()
    i = 1  # start indices at 1
    if aln_tokens == [(None, None)]:
        pass  # nothing to do
    elif refattr is not None and algn_tier is not None:
        attrs[refattr] = algn_tier.id
        algn_data = zip_longest(algn_tier.items, aln_tokens)
        for tgt_item, src_data in algn_data:
            tgt_tok, src_toks = src_data
            for s in src_toks:
                items.append(
                    Item(id='{}{}'.format(tier_id, i),
                         text=s,
                         attributes={refattr:tgt_item.id})
                )
                i += 1
    else:
        for tgt, src in aln_tokens:
            for s in src:
                items.append(Item(id='{}{}'.format(tier_id, i), text=s))
                i += 1
    return Tier(id=tier_id, type=tier_type, items=items, attributes=attrs)
