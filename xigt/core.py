import re
from collections import OrderedDict

class XigtMixin(object):
    def __iter__(self):
        return iter(self._list)

    def __getitem__(self, obj_id):
        try:
            # attempt list indexing
            obj_id = int(obj_id)
            return self._list[obj_id]
        except ValueError:
            return self._dict[obj_id]

    def get(self, obj_id, default=None):
        try:
            return self[obj_id]
        except (KeyError, IndexError):
            return default

class XigtCorpus(XigtMixin):
    def __init__(self, id=None, attributes=None, metadata=None, igts=None):
        self.id = id
        self.attributes = attributes or {}
        self.metadata = metadata
        self._list = igts or []
        self._dict = {}
        for igt in self._list:
            igt.corpus = self
            if igt.id is None: continue
            if igt.id in self._dict:
                raise ValueError('Igt id "{}" already exists in XigtCorpus'
                                 .format(igt.id))
            self._dict[igt.id] = igt

    @property
    def igts(self):
        return self._list

class Igt(XigtMixin):
    def __init__(self, id=None, attributes=None, corpus=None,
                 metadata=None, tiers=None):
        self.id = id
        self.attributes = attributes or {}
        self.corpus = corpus
        self.metadata = metadata
        self._list = tiers or []
        self._dict = {}
        for tier in self._list:
            tier.igt = self
            if tier.id is None: continue
            if tier.id in self._dict:
                raise ValueError('Tier id "{}" already exists in Igt'
                                 .format(tier.id))
            self._dict[tier.id] = tier

    @property
    def tiers(self):
        return self._list

class Tier(XigtMixin):
    def __init__(self, type=None, id=None, ref=None, igt=None,
                 metadata=None, attributes=None, items=None):
        self.type = type
        self.id = id
        self.ref = ref
        self.igt = igt
        self.metadata = metadata
        self.attributes = attributes or {}
        self._list = items or []
        self._dict = {}
        for item in self._list:
            item.tier = self
            if item.id is None: continue
            if item.id in self._dict:
                raise ValueError('Item id "{}" already exists in Tier'
                                 .format(item.id))
            self._dict[item.id] = item

    def __repr__(self):
        return 'Tier({},{},{},[{}])'.format(            
            str(self.type), str(self.id), str(self.ref), ','.join(self.items))

    @property
    def items(self):
        return self._list

    @property
    def reftier(self):
        if self.ref is not None and self.igt is not None:
            return self.igt.get(self.ref)
        else:
            #TODO log this
            return None

class Item(object):
    def __init__(self, type=None, id=None, ref=None, tier=None,
                 attributes=None, content=None):
        self.type = type
        self.id = id
        self.ref = ref
        self.tier = tier # mainly used for alignment expressions
        self.attributes = attributes or {}
        self.content = content

    def __repr__(self):
        return 'Item({},{},{},{})'.format(
            map(str, [self.type, self.id, self.ref, self.content]))

    def __str__(self):
        return str(self.content)

    def resolve_ref(self):
        if self.ref is not None and self.tier is not None:
            return resolve_alignment_expression(self.ref, self.tier.reftier)
        else:
            return None #TODO log this

    def span(self, start, end):
        if self.content is None:
            return None
        return self.content[start:end]

class Metadata(object):
    def __init__(self, type=None, attributes=None, content=None):
        self.type = type
        self.attributes = attributes or {}
        self.content = content

    def __repr__(self):
        return 'Metadata({},"{}")'.format(str(self.type), self.content)

### Alignment Expressions ####################################################

# Module variables
algnexpr_re = re.compile(r'(([a-zA-Z][\-.\w]*)(\[[^\]]*\])?|\+|,)')
selection_re = re.compile(r'(-?\d+:-?\d+|\+|,)')

delim1 = ''
delim2 = ' '

def resolve_alignment_expression(expression, tier, plus=delim1, comma=delim2):
    alignments = algnexpr_re.findall(expression)
    parts = [plus if match == '+' else
             comma if match == ',' else
             resolve_alignment(tier, item_id, selection)
             for match, item_id, selection in alignments]
    return ''.join(parts)

def resolve_alignment(tier, item_id, selection, plus=delim1, comma=delim2):
    item = tier.get(item_id)
    if selection == '':
        return item.content
    spans = selection_re.findall(selection)
    parts = [plus if match == '+' else
             comma if match == ',' else
             item.span(*map(int, match.split(':')))
             for match in spans]
    return ''.join(parts)
