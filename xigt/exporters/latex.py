
from __future__ import print_function
import re
import logging
from itertools import groupby, chain
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
from collections import deque
from xigt import ref
from xigt.exporters.util import sub

DEFAULT_TIER_TYPES = ('words', 'morphemes', 'glosses')
# order matters here
LATEX_CHARMAP = [
    ('\\', '\\textbackslash'),
    ('&', '\\&'),
    ('%', '\\%'),
    ('$', '\\$'),
    ('#', '\\#'),
    ('_', '\\_'),
    ('{', '\\{'),
    ('}', '\\}'),
    ('~', '\\textasciitilde'),
    ('^', '\\textasciicircum'),
]

header = '''
\\documentclass{article}
\\usepackage{gb4e}
\\begin{document}
'''

footer = '''
\\end{document}
'''

def xigt_export(xc, outpath, config=None):
    config = prepare_config(config)
    with open(outpath, 'w') as out_fh:
        print(header, file=out_fh)
        for s in export_corpus(xc, config):
            print(s, file=out_fh)
            print('', file=out_fh)  # separate with a blank line
        print(footer, file=out_fh)

def prepare_config(config):
    if config is None:
        config = {}
    config.setdefault('tier_types', DEFAULT_TIER_TYPES)
    config.setdefault('item_substitutions', [])
    config.setdefault('tier_substitutions', [])
    return config

def escape(s):
    # consider a re sub with a function. e.g.
    # _character_unescapes = {'\\s': _field_delimiter, '\\n': '\n', '\\\\': '\\'}
    # _unescape_func = lambda m: _character_unescapes[m.group(0)]
    # _unescape_re = re.compile(r'(\\s|\\n|\\\\)')
    # _unescape_re.sub(_unescape_func, string, re.UNICODE)
    for c, r in LATEX_CHARMAP:
        s = s.replace(c, r)
    return s

def export_corpus(xc, config):
    for igt in xc:
        logging.debug('Exporting {}'.format(str(igt.id)))
        x = export_igt(igt, config)
        yield x

def export_igt(igt, config):
    tier_types = config['tier_types']
    item_subs = config['item_substitutions']
    tier_subs = config['tier_substitutions']
    tiers = []
    for tier in igt.tiers:
        typ = tier.type
        if typ is not None and typ.lower() in tier_types:
            tiers.append(tier)
    if len(tiers) < 2:
        return '%\n% cannot export IGT {}\n%'.format(igt.id)
    logging.debug('Aligning tiers: {}'.format(', '.join(t.id for t in tiers)))
    lines = []
    all_groups = group_alignments(tiers)
    for col in all_groups:
        logging.debug('Col {}'.format([[i.id for i in r] for r in col]))
    lines.append('\\begin{exe}\\small')
    lines.append('\\ex\\g{}'.format('l' * len(tiers)))
    depth = len(all_groups[0])
    for i in range(depth):
        toks = []
        tier_type = tiers[i].type
        for col in all_groups:
            items = col[i]
            toks.append('{{{}}}'.format(
                ' '.join(
                    sub(escape(item.get_content() or '{}'),
                        tier_type,
                        item_subs)
                    for item in items
                )
            ))
        lines.append(sub(' '.join(toks) + '\\\\', tier_type, tier_subs))
    # add translation
    for tier in igt.tiers:
        if tier.type == 'translations' and len(tier) > 0:
            lines.append('\\trans {}'.format(
                sub(escape(tier[0].get_content() or '{}'),
                    tier.type,
                    tier_subs)
            ))
    lines.append('\\end{exe}')
    return '\n'.join(lines)


def group_alignments(tiers):
    # trellis has positions with tokens or each row:
    #    visualized as a grid:
    # [ [ [w1..] ]  [ [w2..] ]  ... ]
    # | | [m1..] |  | [m2..] |  ... |
    # [ [ [g1..] ], [ [g2..] ], ... ]
    #    or as a list
    # [columns [rows [tokens]]]
    trellis = [[[item]] for item in tiers[0].items]
    for tier in tiers[1:]:
        trellis = align_tier(trellis, tier)
    return trellis


def align_tier(trellis, tier):
    depth = len(trellis[0])
    agenda = get_agenda(tier) # list of (aligned ids, item)
    delay = deque()  # when we need to postpone an agendum
    idx = -1  # current trellis position
    idxmap = build_idxmap(trellis, depth - 1) # regen when trellis size changes
    for agendum in agenda:
        ids, items = agendum
        logging.debug('Agendum: {} -> {}'.format([i.id for i in items], ids))
        debug_display_trellis(trellis)
        # no alignment
        if not ids:
            logging.debug('Delay')
            delay.append(agendum)
            continue
        # assumes ids are ordered
        start = idxmap[ids[0]]
        end = idxmap[ids[-1]]
        logging.debug('idx: {}\tstart: {}\tend: {}\tdepth: {}'
                      .format(idx, start, end, depth))
        # if the next aligned thing is ahead of idx, move ahead
        while idx < start:
            idx += 1
            trellis[idx].append([])
            logging.debug('Added row at idx {}'.format(idx))
        # now fill in from delayed agenda
        if delay:
            trellis, num = add_delayed(trellis, delay, start, depth)
            # this changed the size, so shift all indices up by num
            idx += num
            start += num
            end += num
            idxmap = build_idxmap(trellis, depth - 1)
        # now add new item, merging if necessary
        if start != end:
            # end + 1 so the slice gets the last column
            trellis = merge_columns(trellis, start, end + 1)
            idxmap = build_idxmap(trellis, depth - 1)
            debug_display_trellis(trellis)
        #trellis[idx]
        #trellis[idx][depth]
        trellis[idx][depth].extend(items)
        logging.debug('Added items at idx {} depth {}: {}'
                      .format(idx, depth, items))
    # when agendum is done, just append any remaining delayed items
    trellis, _ = add_delayed(trellis, delay, len(trellis), depth)
    # if the agenda was shorter than the prev tier, fill in empty values
    idx += 1
    while idx < len(trellis):
        logging.debug('Filling in empty slot at idx {}'.format(idx))
        trellis[idx].append([])
        idx += 1
    logging.debug('Agenda done.')
    for col in trellis:
        logging.debug('Col {}'.format(col))
    return trellis

def get_agenda(tier):
    agenda = [(ref.ids(item.alignment or item.segmentation), item)
              for item in tier.items]
    # then group those with the same alignment (still a list [(ids, item)])
    agenda = deque(tuple([k, [g[1] for g in gs]])
                   for k, gs in groupby(agenda, key=lambda x: x[0]))
    return agenda

def build_idxmap(trellis, depth):
    idxmap = {it.id:i for i, col in enumerate(trellis) for it in col[depth]}
    logging.debug('Built idxmap for depth {}:\n  {}'.format(depth, idxmap))
    return idxmap

def add_delayed(trellis, delay, pos, depth):
    num = 0
    while delay:
        _, delayed_items = delay.popleft()
        col = [[]] * (depth)
        col.append(delayed_items)
        trellis.insert(pos, col)
        logging.debug('Added delayed items at {}: {}'
                      .format(pos, delayed_items))
        num += 1
    return trellis, num

def merge_columns(trellis, start, end):
    logging.debug('Merging columns {}:{}'.format(start, end-1))
    return (
        trellis[:start] +
        # too bad we need that ugly map(list...) in there :(
        [list(map(list,
                  map(chain.from_iterable,
                      zip_longest(*trellis[start:end], fillvalue=[]))))
        ] +
        trellis[end:]
    )

def debug_display_trellis(trellis):
    strs = []
    for col in trellis:
        toks = [' '.join(i.id for i in row) if row else '[]' for row in col]
        maxlen = max(len(t) for t in toks)
        toks = [t.ljust(maxlen) for t in toks]
        strs.append(toks)
    logging.debug(
        'Trellis:\n' +
        '\n'.join(' | '.join(toks)
                  for toks in zip_longest(*strs, fillvalue='--'))
    )
