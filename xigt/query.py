
from collections import deque
from itertools import chain

from xigt.consts import (
    ALIGNMENT,
    CONTENT,
    SEGMENTATION
)

from xigt import ref

def ancestors(obj, refattrs=(ALIGNMENT, SEGMENTATION)):
    """
    >>> for anc in query.ancestors(igt.get_item('g1'), refattrs=(ALIGNMENT, SEGMENTATION)):
    ...     print(anc)
    (<Tier object (id: g type: glosses) at ...>, 'alignment', <Tier object (id: m type: morphemes) at ...>, [<Item object (id: m1) at ...>])
    (<Tier object (id: m type: morphemes) at ...>, 'segmentation', <Tier object (id: w type: words) at ...>, [<Item object (id: w1) at ...>])
    (<Tier object (id: w type: words) at ...>, 'segmentation', <Tier object (id: p type: phrases) at ...>, [<Item object (id: p1) at ...>])
    """
    if hasattr(obj, 'tier'):
        tier = obj.tier
        items = [obj]
    else:
        tier = obj
        items = tier.items
    while True:
        # get the first specified attribute
        refattr = next((ra for ra in refattrs if ra in tier.attributes), None)
        if not refattr:
            break
        reftier = ref.dereference(tier, refattr)
        ids = set(chain.from_iterable(
            ref.ids(item.attributes.get(refattr, '')) for item in items
        ))
        refitems = [item for item in reftier.items if item.id in ids]
        yield (tier, refattr, reftier, refitems)
        tier = reftier
        items = refitems


def descendants(obj, refattrs=(SEGMENTATION, ALIGNMENT), follow='first'):
    """
    >>> for des in query.descendants(igt.get_item('p1'), refattrs=(SEGMENTATION, ALIGNMENT)):
    ...     print(des)
    (<Tier object (id: p type: phrases) at ...>, 'segmentation', <Tier object (id: w type: words) at ...>, [<Item object (id: w1) at ...>])
    (<Tier object (id: p type: phrases) at ...>, 'alignment', <Tier object (id: t type: translations) at ...>, [<Item object (id: t1) at ...>])
    (<Tier object (id: w type: words) at ...>, 'segmentation', <Tier object (id: m type: morphemes) at ...>, [<Item object (id: m1) at ...>])
    (<Tier object (id: m type: morphemes) at ...>, 'alignment', <Tier object (id: g type: glosses) at ...>, [<Item object (id: g1) at ...>])
    """

    if hasattr(obj, 'tier'):
        tier = obj.tier
        items = [obj]
    else:
        tier = obj
        items = tier.items
    igt = tier.igt
    visited = set()
    agenda = deque([(tier, items)])
    while agenda:
        tier, items = agenda.popleft()
        tier_refs = tier.referrers(refattrs)
        item_ids = set(item.id for item in items)
        # get followable refattrs with something on the referrers list
        ras = [ra for ra in refattrs if tier_refs[ra]]
        if follow == 'first' and ras:
            ras = [ras[0]]
        if not ras:
            continue
        # unlike ancestors, descendants for a refattr may have 1+ tiers
        for refattr in ras:
            # try to avoid cycles
            if (tier.id, refattr) in visited:
                continue
            else:
                visited.add((tier.id, refattr))
            for reftier_id in tier_refs[refattr]:
                reftier = igt[reftier_id]
                refitems = [
                    item for item in reftier.items
                    if set(ref.ids(item.attributes.get(refattr,'')))
                       .intersection(item_ids)
                ]
                yield (tier, refattr, reftier, refitems)
                agenda.append((reftier, refitems))

#def ingroup(obj, refattrs)
#def filter([objs], lambda x: