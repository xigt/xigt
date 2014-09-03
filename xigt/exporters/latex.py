
from itertools import groupby, takewhile, chain
from collections import deque
from xigt.core import get_alignment_expression_ids

DEFAULT_TIER_TYPES = ('words', 'morphemes', 'glosses')

# \gll
# one {} two three {four five}\\
# {}  X  {two-a two-b} three four.five \\
# \glt ``blah''

# w1    w2    w3          w4    w5
# m1=w1 m2    m3=w3 m4=w3 m5=w4 m6=w5 m7
# g1=m1 g2=m2 g3=m3 g4=m4 g5=m5:m6    g6=m7 g7=m7

def export_corpus(xc):
    for igt in xc.igts:
        print(export_igt(igt))
        print()  # blank line to separate

def export_igt(igt):
    tiers = []
    for tier in igt.tiers:
        typ = tier.type
        if typ is not None and typ.lower() in DEFAULT_TIER_TYPES:
            tiers.append(tier)
    if len(tiers) < 2:
        return '---'
    all_groups = group_alignments(tiers)
    print('\\begin{exe}')
    print('\\ex\\g{}'.format('l' * len(tiers)))
    depth = len(all_groups[0])
    for i in range(depth):
        toks = []
        for col in all_groups:
            items = col[i]
            if len(items) == 1:
                toks.append(items[0].get_content())
            else:
                toks.append('{{{}}}'.format(' '.join(item.get_content()
                                                     for item in items)))
        print(' '.join(toks), '\\\\')
    # add translation
    for tier in igt.tiers:
        if tier.type == 'translations':
            print('\\trans {}'.format(tier[0].get_content()))
    print('\\end{exe}')


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
    agenda = [(get_alignment_expression_ids(item.alignment), item)
              for item in tier.items]
    # then group those with the same alignment (still a list [(ids, item)])
    agenda = deque(tuple([k, [g[1] for g in gs]])
                   for k, gs in groupby(agenda, key=lambda x: x[0]))
    delay = deque()  # when we need to postpone an agendum
    idx = 0  # current trellis position
    for agendum in agenda:
        ids, items = agendum
        # no alignment
        if not ids:
            delay.append(agendum)
            continue
        # unfortunately need to regenerate this when size changes
        idxmap = {it.id:i for i, col in enumerate(trellis)
                          for it in col[depth-1]}
        # assumes ids are ordered
        start = idxmap[ids[0]]
        end = idxmap[ids[-1]]
        # if start is just the next element, just increment
        if start > idx:
            idx += 1
        # otherwise pad skipped columns
        while idx < start:
            trellis[idx].append([])
            idx += 1
        # now fill in from delayed agenda
        while delay:
            _, delayed_items = delay.popleft()
            col = [[]] * (depth)
            col.append(delayed_items)
            trellis.insert(start, col)
            idx += 1
        # now add new item, merging if necessary
        if start != end:
            trellis = (trellis[:start] +
                       [merge(trellis[start:end+1])] +
                       trellis[end+1:])
        trellis[idx].append(items)
    # just add any left over
    for agendum in delay:
        _, delayed_items = agendum
        col = [[]] * (depth)
        col.append(delayed_items)
        trellis.append(col)
    return trellis

def merge(cols):
    # too bad we need that ugly map(list...) in there :(
    return list(map(list, map(chain.from_iterable, zip(*cols))))