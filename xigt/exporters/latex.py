
import re
import logging
from itertools import groupby, takewhile, chain
from collections import deque
from xigt.core import get_alignment_expression_ids

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

# \gll
# one {} two three {four five}\\
# {}  X  {two-a two-b} three four.five \\
# \glt ``blah''

# w1    w2    w3          w4    w5
# m1=w1 m2    m3=w3 m4=w3 m5=w4 m6=w5 m7
# g1=m1 g2=m2 g3=m3 g4=m4 g5=m5:m6    g6=m7 g7=m7

def xigt_export(xc, out_fh, strmap=None):
    print(header, file=out_fh)
    for s in export_corpus(xc, strmap=strmap):
        print(s, file=out_fh)
        print('', file=out_fh)  # separate with a blank line
    print(footer, file=out_fh)

def escape(s, strmap):
    # consider a re sub with a function. e.g.
    # _character_unescapes = {'\\s': _field_delimiter, '\\n': '\n', '\\\\': '\\'}
    # _unescape_func = lambda m: _character_unescapes[m.group(0)]
    # _unescape_re = re.compile(r'(\\s|\\n|\\\\)')
    # _unescape_re.sub(_unescape_func, string, re.UNICODE)
    for c, r in LATEX_CHARMAP:
        s = s.replace(c, r)
    for c in strmap:
        pat = strmap[c]
        if isinstance(pat, str):
            s = re.sub(c, strmap[c], s)
        elif len(pat) == 2:
            f = eval('lambda {}: {}'.format(*pat))
            s = re.sub(c, f, s)
    return s

def export_corpus(xc, strmap=None):
    for igt in xc:
        logging.debug('Exporting {}'.format(str(igt.id)))
        x = export_igt(igt, strmap=strmap)
        yield x

def export_igt(igt, strmap=None):
    strmap = strmap or {}
    tiers = []
    for tier in igt.tiers:
        typ = tier.type
        if typ is not None and typ.lower() in DEFAULT_TIER_TYPES:
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
        for col in all_groups:
            items = col[i]
            if len(items) == 1:
                toks.append(escape(items[0].get_content(), strmap))
            else:
                toks.append('{{{}}}'.format(
                    ' '.join(escape(item.get_content(), strmap)
                             for item in items)
                ))
        lines.append(' '.join(toks) + '\\\\')
    # add translation
    for tier in igt.tiers:
        if tier.type == 'translations':
            lines.append('\\trans {}'.format(
                escape(tier[0].get_content(), strmap)
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
    # get list of (aligned ids, item)
    agenda = get_agenda(tier)
    delay = deque()  # when we need to postpone an agendum
    idx = -1  # current trellis position
    # unfortunately need to regenerate this when size changes
    idxmap = build_idxmap(trellis, depth - 1)
    for agendum in agenda:
        ids, items = agendum
        logging.debug('Agendum: {} -> {}'.format([i.id for i in items], ids))
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
            logging.debug('Added row at {}'.format(idx))
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
        trellis[idx][depth].extend(items)
        logging.debug('Added items at {} depth {}: {}'
                      .format(idx, depth - 1, items))
    # when agendum is done, just append any remaining delayed items
    trellis, _ = add_delayed(trellis, delay, len(trellis), depth)
    logging.debug('Agenda done.')
    for col in trellis:
        logging.debug('Col {}'.format(col))
    return trellis

def get_agenda(tier):
    agenda = [(get_alignment_expression_ids(item.alignment), item)
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
    return (
        trellis[:start] +
        # too bad we need that ugly map(list...) in there :(
        [list(map(list, map(chain.from_iterable,
                            zip(*trellis[start:end]))))] +
        trellis[end:]
    )