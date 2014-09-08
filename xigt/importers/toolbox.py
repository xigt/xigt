#!/usr/bin/env python3

from collections import OrderedDict
from itertools import zip_longest
import logging
from xigt import (XigtCorpus, Igt, Tier, Item, Metadata, Meta)
from xigt.codecs import xigtxml

try:
    import toolbox
except ImportError:
    import sys
    print('Could not import Toolbox module. Get it from here:\n'
          '  https://github.com/goodmami/toolbox\n',
          file=sys.stderr)


class XigtImportError(Exception):
    pass


def xigt_import(in_fh, out_fh):
    tb = toolbox.read_toolbox_file(in_fh)
    igts = toolbox_igts(tb)  # TODO: include options, like mkrPriKey
    xc = XigtCorpus(igts=igts, mode='transient')
    xigtxml.dump(out_fh, xc)


def toolbox_igts(tb):
    cps_id = None
    ref = None
    for event, result in toolbox.item_iter(tb, keys=set(['\\id', '\\ref'])):
        if event == 'key':
            mkr, val = result
            if mkr == '\\ref':
                ref = val
            elif mkr == '\\id':
                cps_id = val
                ref = None
        elif event == 'item':
            if ref is None:
                # don't yet know what to do with header info
                continue
            igt = make_igt(cps_id, ref, result)
            if igt is not None:
                yield igt


def make_igt(cps_id, ref, data,
             tier_types={'\\t': 'words', '\\m': 'morphemes',
                         '\\g': 'glosses', '\\p': 'pos',
                         '\\f': 'translations'},
             alignments={'\\m': '\\t', '\\g': '\\m', '\\p': '\\m'}):
    attrs = {}
    if cps_id is not None:
        attrs['corpus-id'] = cps_id
    metadata = None
    try:
        tiers = make_all_tiers(data, tier_types, alignments)
        igt = Igt(id=ref, attributes=attrs, metadata=metadata, tiers=tiers)
    except XigtImportError as ex:
        logging.error('Error during import of item {}:\n  {}'
                      .format(ref, str(ex)))
        igt = None
    finally:
        return igt


def make_all_tiers(item_data, tier_types, alignments):
    aligned_tiers = set(alignments.keys()).union(alignments.values())
    tier_data = toolbox.normalize_item(item_data, aligned_tiers)
    prev = {}
    for mkr, aligned_tokens in toolbox.align_tiers(tier_data, alignments):
        tier_type = tier_types.get(mkr)
        tier_id = mkr.lstrip('\\')
        algn_tier = prev.get(alignments.get(mkr))  # could be None
        try:
            tier = make_tier(tier_type, tier_id, aligned_tokens, algn_tier)
        except (AttributeError, AssertionError):
            raise XigtImportError('Error making {} tier (marker: {}).'
                                  .format(tier_type, mkr))
        prev[mkr] = tier
        yield tier

def make_tier(tier_type, tier_id, aligned_tokens, algn_tier):
    attrs = OrderedDict()
    items = list()
    i = 1  # start indices at 1
    if aligned_tokens == [(None, None)]:
        pass  # nothing to do
    elif algn_tier is not None:
        attrs['alignment'] = algn_tier.id
        algn_data = zip_longest(algn_tier.items, aligned_tokens)
        for tgt_item, src_data in algn_data:
            tgt_tok, src_toks = src_data
            assert tgt_tok == tgt_item.text  # FIXME is this necessary?
            for s in src_toks:
                items.append(
                    Item(id='{}{}'.format(tier_id, i),
                         text=s,
                         attributes={'alignment':tgt_item.id})
                )
                i += 1
    else:
        for tgt, src in aligned_tokens:
            for s in src:
                items.append(Item(id='{}{}'.format(tier_id, i), text=s))
                i += 1
    return Tier(id=tier_id, type=tier_type, items=items, attributes=attrs)