
from xigt.consts import (
    ALIGNMENT,
    CONTENT,
    SEGMENTATION
)

def ancestors(obj, refattrs=(ALIGNMENT, SEGMENTATION)):
    """
    Return a mapping of {tier_id: selections} where selections is a list
    of [(item_id, spans)] and spans is a list of (start, end) tuples.
    e.g.
    >>> query.ancestors(igt.get_item('g1'), refattrs=(ALIGNMENT, SEGMENTATION))
    {
      "m": [("m1", (None, None))],
      "w": [("w1", (0, 3))],
      "p": [("p1", (0, 5))]
    }
    """
    anc = {}
    for refattr in refattrs:
        if refattr in obj.attributes:

            anc = _ancestors(obj)
    return anc or {}


def descendants(obj, refattrs=(ALIGNMENT, SEGMENTATION)):
    pass


def ascend(obj, refattrs):
    pass

def descend(obj, refattrs):
    pass

#def ingroup(obj, refattrs)
#def filter([objs], lambda x: 