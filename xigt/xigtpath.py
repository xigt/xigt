
import re
from collections import namedtuple, deque
from itertools import chain

from xigt import XigtCorpus, Meta, MetaChild
from xigt.errors import XigtError


class XigtPathError(XigtError): pass

xp_tokenizer_re = re.compile(
    r'"(?:\\.|[^\\"])*"|'  # double-quoted strings (allow escaped quotes \")
    r'//?|'  # // descendant-or-self or / descendant
    r'\.\.?|'  # .. parent or . self axes
    r'@|'  # attribute axis
    r'\[|\]|'  # predicate
    r'\(|\)|'  # groups
    r'!=|=|'  # comparisons
    r'(?:text|value|referents|referrers|ancestors|descendants)\([^)]*\)|'
    r'\*|[^.\/\[\]!=]+'  # .., *, igt, tier, item, etc.
)

def find(obj, path):
    return next(iterfind(obj, path), None)

def findall(obj, path):
    return list(iterfind(obj, path))

def iterfind(obj, path):
    if path.endswith('/'):
        raise XigtPathError('XigtPaths cannot end with "/"')
    steps = deque(xp_tokenizer_re.findall(path))
    if not steps:
        return
    # elif steps[0] == '(':  # handle disjunctions here eventually
    if steps[0] in ('/', '//'):
        if steps[0] == '/':
            steps.popleft()
        results = _step([_get_corpus(obj)], steps)
    else:
        results = _step([obj], steps)
    for result in results:
        yield result

def _step(objs, steps):
    if not steps:
        for obj in objs:
            yield obj
    else:
        step = steps.popleft()
        # axis and nodetests
        if step == '//':
            name = steps.popleft()
            results = (d for obj in objs
                         for d in _find_descendant_or_self(obj, name))
        elif step == '@':
            attr = steps.popleft()
            results = (res for obj in objs for res in _find_attr(obj, attr))
        elif step == '..':
            results = (obj._parent for obj in objs)
        elif step == '.':
            results = objs
        else:
            results = (res for obj in objs for res in _find_child(obj, step))
        # predicates
        while steps and steps[0] == '[':
            predtest = _make_predicate_test(steps)
            results = filter(predtest, results)
        if steps:
            if steps[0] in ('/', '//'):
                if steps[0] == '/':
                    steps.popleft()
                results = _step(results, steps)
            else:
                raise XigtPathError('Subpath has no valid initial delimiter:',
                                    ''.join(steps))
        for obj in results:
            yield obj

def _find_child(obj, name):
    results = []
    if name == '*' and hasattr(obj, '__iter__'):
        results = iter(obj)
    elif name == 'igt' and hasattr(obj, 'igts'):
        results = iter(obj.igts)
    elif name == 'tier' and hasattr(obj, 'tiers'):
        results = iter(obj.tiers)
    elif name == 'item' and hasattr(obj, 'items'):
        results = iter(obj.items)
    elif name == 'metadata' and hasattr(obj, 'metadata'):
        results = iter(obj.metadata)
    elif name == 'meta' and hasattr(obj, 'metas'):
        results = iter(obj.metas)
    elif isinstance(obj, (Meta, MetaChild)):
        results = (mc for mc in obj if getattr(mc, 'name', None) == name)
    elif name == 'text()':
        results = [obj.text]
    elif name == 'value()':
        results = [obj.value()]
    for res in results:
        yield res

def _find_attr(obj, attr):
    val = None
    if attr in ('type', 'id', 'name'):
        val = getattr(obj, attr, None)
    if val is None:
        val = obj.attributes.get(attr, None)
    if val is not None:
        yield val

def _find_descendant_or_self(obj, name):
    if isinstance(obj, MetaChild):
        objname = obj.name
    else:
        objname = obj.__class__.__name__.lower()
    if objname == name:
        yield obj
    for child in _find_child(obj, '*'):
        for desc in _find_descendant_or_self(child, name):
            yield desc

def _make_predicate_test(steps):
    steps.popleft()  # '['
    # parse expr here?
    subpath = deque()
    while steps[0] not in (']', '=', '!='):
        subpath.append(steps.popleft())
    subpath = ''.join(subpath)  # ugly hack so findall() works
    if steps[0] == ']':
        predtest = lambda obj: any(bool(findall(obj, subpath)))
    elif steps[0] in ('=', '!='):
        cmp = steps.popleft()
        val = steps.popleft().strip('"')
        if cmp == '=':
            predtest = lambda obj: any(v==val for v in findall(obj, subpath))
        elif cmp == '!=':
            predtest = lambda obj: all(v!=val for v in findall(obj, subpath))
    steps.popleft()  # ']'
    return predtest

def _get_corpus(obj):
    while not isinstance(obj, XigtCorpus):
        obj = obj._parent
    return obj
