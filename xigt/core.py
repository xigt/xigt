import re
from collections import OrderedDict

class XigtMixin(object):
    def __getitem__(self, obj_id):
        try:
            # attempt list indexing
            obj_id = int(obj_id)
            return list(self._data.values())[obj_id]
        except ValueError:
            return self.get(obj_id)

    def get(self, tier_id, default=None):
        return self._data.get(tier_id, default)

class XigtCorpus(XigtMixin):
    def __init__(self, id=None, attributes=None, metadata=None, igts=None):
        self.id = id
        self.attributes = attributes or {}
        self.metadata = metadata
        self._data = OrderedDict()
        for i, igt in enumerate(igts):
            igt.corpus = self
            self._data[igt.id or 'igt{}'.format(i)] = igt

    @property
    def igts(self):
        return list(self._data.values())

class Igt(XigtMixin):
    def __init__(self, id=None, attributes=None, corpus=None,
                 metadata=None, tiers=None):
        self.id = id
        self.attributes = attributes = {}
        self.corpus = corpus
        self.metadata = metadata
        self._data = OrderedDict()
        for i, tier in enumerate(tiers):
            tier.igt = self
            self._data[tier.id or 'tier{}'.format(i)] = tier

    @property
    def tiers(self):
        return list(self._data.values())

class Tier(XigtMixin):
    def __init__(self, type=None, id=None, ref=None, igt=None,
                 metadata=None, attributes=None, items=None):
        self.type = type
        self.id = id
        self.ref = ref
        self.igt = igt
        self.metadata = metadata
        self.attributes = attributes or {}
        self._data = OrderedDict()
        for i, item in enumerate(items or []):
            item.tier = self
            self._data[item.id or 'item{}'.format(i)] = item

    def __repr__(self):
        return 'Tier({},{},{},[{}])'.format(
            str(self.type) if self.type is not None else 'Basic',
            str(self.id) if self.id is not None else '?',
            str(self.ref) if self.ref is not None else '?',
            ','.join(self.items))

    @property
    def items(self):
        return list(self._data.values())

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
            str(self.type) if self.type is not None else 'Basic',
            str(self.id) if self.id is not None else '?',
            str(self.ref) if self.ref is not None else '?',
            str(self.content))

    def __str__(self):
        return str(self.content)

    def resolve_ref(self):
        if self.ref is not None and self.tier is not None:
            return resolve_alignment_expression(self.ref, self.tier.reftier)
        else:
            return None #TODO log this

    def span(self, start, end):
        return self.content[start:end]

class Metadata(object):
    def __init__(self, type=None, attributes=None, content=None):
        self.type = type
        self.attributes = attributes or {}
        self.content = content

    def __repr__(self):
        return 'Metadata({},"{}")'.format(self.type or 'Basic', self.content)

### Alignment Expressions ####################################################

# Module variables
algnexpr_re = re.compile(r'(([a-zA-Z][\-.\w]*)(\[[^\]]*\])?|\+|,)')
selection_re = re.compile(r'(-?\d+:-?\d+|\+|,)')

plus = ''
comma = ' '

def resolve_alignment_expression(expression, tier, plus=plus, comma=comma):
    alignments = algnexpr_re.findall(expression)
    parts = [plus_delimiter if match == '+' else
             comma_delimiter if match == ',' else
             resolve_alignment(tier, item_id, selection)
             for match, item_id, selection in alignments]
    return ''.join(parts)

def resolve_alignment(tier, item_id, selection, plus=plus, comma=comma):
    item = tier.get(item_id)
    if selection == '':
        return item.content
    spans = selection_re.findall(selection)
    parts = [plus_delimiter if match == '+' else
             comma_delimiter if match == ',' else
             item.span(*map(int, match.split(':')))
             for match in spans]
    return ''.join(parts)
