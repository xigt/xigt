import re
from collections import OrderedDict

class XigtMixin(object):
    """
    Common methods for accessing subelements in XigtCorpus, Igt, and
    Tier objects.
    """
    def __init__(self):
        self._list = []
        self._dict = OrderedDict()

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

    def add(self, obj):
        obj._parent = self
        if obj.id is not None:
            if obj.id in self._dict:
                raise ValueError('Id "{}" already exists in collection.'
                                 .format(obj.id))
            self._dict[obj.id] = obj
        self._list.append(obj)

    def add_list(self, objs):
        if objs is not None:
            for obj in objs:
                self.add(obj)

class XigtInheritanceMixin(object):
    """
    Enables the inheritance of attributes and metadata.
    """
    def __init__(self):
        self._local_attrs = set()

    def get_attribute(self, key, inherit=True):
        if key in self.attributes:
            return self.attributes[key]
        elif inherit and hasattr(self, _parent) and self._parent is not None:
            return self._parent.get_attribute(key, inherit=inherit)
        else:
            return None

    def get_meta(self, key, inherit=True):
        pass # what to do here?

class XigtCorpus(XigtMixin):
    """
    A container of Igt objects, as well as corpus-level attributes and
    metadata. In serialization formats (e.g. XigtXML), XigtCorpus
    becomes the root element.
    """
    def __init__(self, id=None, attributes=None, metadata=None, igts=None):
        XigtMixin.__init__(self)
        self.id = id
        self.attributes = attributes or OrderedDict()
        self.metadata = metadata
        self.add_list(igts)

    @property
    def igts(self):
        return self._list

    @igts.setter
    def igts(self, value):
        self._list = value

class Igt(XigtMixin):
    """
    An IGT (Interlinear Glossed Text) instance.
    """
    def __init__(self, id=None, type=None, attributes=None, metadata=None,
                 tiers=None, corpus=None):
        XigtMixin.__init__(self)
        self.id = id
        self.type = type
        self.attributes = attributes or OrderedDict()
        self.metadata = metadata
        self.add_list(tiers)
        self._parent = corpus

    @property
    def corpus(self):
        return self._parent

    @property
    def tiers(self):
        return self._list

    @tiers.setter
    def tiers(self, value):
        self._list = value

class Tier(XigtMixin):
    """
    A tier of IGT data. A tier should contain homogenous Items of
    data, such as all words or all glosses.
    """
    def __init__(self, id=None, ref=None, type=None, attributes=None,
                 metadata=None, items=None, igt=None):
        XigtMixin.__init__(self)
        self.id = id
        self.ref = ref
        self.type = type
        self.attributes = attributes or OrderedDict()
        self.metadata = metadata
        self.add_list(items)
        self._parent = igt

    def __repr__(self):
        return 'Tier({},{},{},[{}])'.format(
            str(self.type), str(self.id), str(self.ref), ','.join(self.items))

    @property
    def igt(self):
        return self._parent

    @property
    def items(self):
        return self._list

    @items.setter
    def items(self, value):
        self._list = value

    @property
    def reftier(self):
        if self.ref is not None and self.igt is not None:
            return self.igt.get(self.ref)
        else:
            #TODO log this
            return None

class Item(object):
    """
    A single datum on a Tier. Often these are tokens, such as words
    or glosses, but may be phrases, translations, or (via extensions)
    more complex data like syntax nodes or dependencies.
    """
    def __init__(self, id=None, ref=None, type=None, attributes=None,
                 content=None, tier=None):
        self.id = id
        self.ref = ref
        self.type = type
        self.attributes = attributes or OrderedDict()
        self.content = content
        self._parent = tier # mainly used for alignment expressions

    def __repr__(self):
        return 'Item({},{},{},{})'.format(
            map(str, [self.type, self.id, self.ref, self.content]))

    def __str__(self):
        return str(self.content)

    @property
    def tier(self):
        return self._parent

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
    """
    A container for metadata on XigtCorpus, Igt, or Tier objects.
    Extensions may place constraints on the allowable metadata.
    """
    def __init__(self, type=None, attributes=None, content=None):
        self.type = type
        self.attributes = attributes or OrderedDict()
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
