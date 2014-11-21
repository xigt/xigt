import re
import logging
import warnings
from collections import OrderedDict

# common strings
ALIGNMENT = 'alignment'
CONTENT = 'content'
SEGMENTATION = 'segmentation'

# for auto-alignment
item_delimiters = {
    'words': (' ',),
    'morphemes': ('-', '=', '~'),
    'glosses': ('-', '=', '~')
}


class XigtError(Exception): pass
class XigtStructureError(XigtError): pass
class XigtAttributeError(XigtError): pass
class XigtAutoAlignmentError(XigtError): pass

class XigtWarning(Warning): pass

def _has_parent(obj):
    return hasattr(obj, '_parent') and obj._parent is not None


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

    def __len__(self):
        return len(self._list)

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
        except KeyError:
            logging.debug('Object not found with id {}.'.format(obj_id))
        except IndexError:
            logging.debug('Object not found at position {}.'.format(obj_id))
        return default

    def select(self, id=None, type=None,
               alignment=None, content=None, segmentation=None):
        match = lambda x: (
            (id is None or x.id == id) and
            (type is None or x.type == type) and
            (alignment is None or x.alignment == alignment) and
            (content is None or x.content == content) and
            (segmentation is None or x.segmentation == segmentation)
        )
        return filter(match, self)

    def add(self, obj):
        obj._parent = self
        self._create_id_mapping(obj)
        self._list.append(obj)

    def add_list(self, objs):
        if objs is not None:
            for obj in objs:
                self.add(obj)

    def _create_id_mapping(self, obj):
        if obj.id is not None:
            if obj.id in self._dict:
                warnings.warn(
                    'Id "{}" already exists in collection.'.format(obj.id),
                    XigtWarning
                )
            self._dict[obj.id] = obj

    def refresh_index(self):
        self._dict = OrderedDict()
        for obj in self._list:
            self._create_id_mapping(obj)

    def clear(self):
        self._dict = OrderedDict()
        self._list = []


class XigtAttributeMixin(object):

    def __init__(self, id=None, type=None,
                 alignment=None, content=None, segmentation=None,
                 attributes=None):
        self.id = id
        self.type = type
        # _local_attrs are those that should not be inherited (only valid
        # locally). By default include these pre-defined Xigt attributes.
        self._local_attrs = set([
            'id', 'type', ALIGNMENT, CONTENT, SEGMENTATION
        ])
        self.attributes = OrderedDict()
        # core alignment expression attributes go first
        if alignment is not None:
            self.attributes[ALIGNMENT] = alignment
        if content is not None:
            self.attributes[CONTENT] = content
        if segmentation is not None:
            self.attributes[SEGMENTATION] = segmentation
        # now add the non-AlEx attributes
        self.attributes.update(attributes or {})

    def get_attribute(self, key, default=None, inherit=True):
        try:
            return self.attributes[key]
        except KeyError:
            if not inherit or not _has_parent(self) or key:
                raise
                # raise XigtAttributeError('No attribute {}.'.format(key))
            if key in self._local_attrs:
                return None  # don't inherit local-only attributes
            return self._parent.get_attribute(key, default, inherit)

    @property
    def alignment(self):
        return self.attributes.get(ALIGNMENT)
    @alignment.setter
    def alignment(self, value):
        self.attributes[ALIGNMENT] = value

    @property
    def content(self):
        return self.attributes.get(CONTENT)
    @content.setter
    def content(self, value):
        self.attributes[CONTENT] = value

    @property
    def segmentation(self):
        return self.attributes.get(SEGMENTATION)
    @segmentation.setter
    def segmentation(self, value):
        self.attributes[SEGMENTATION] = value


class XigtMetadataMixin(object):
    """
    Enables the inheritance of metadata.
    """
    def __init__(self, metadata):
        self.metadata = list(metadata or [])

    def get_meta(self, key, conditions=None, default=None, inherit=True):
        if conditions is None:
            conditions = []
        metas = []
        for metadata in self.metadata:
            if metadata.type != 'xigt-meta':
                continue
            for meta in metadata.text:
                if meta.type == key and all(c(meta) for c in conditions):
                    metas.append(meta)
        if metas:
            return metas
        elif inherit and _has_parent(self):
            return self._parent.get_meta(key, conditions, default, inherit)
        else:
            return default


class XigtCorpus(XigtMixin, XigtAttributeMixin, XigtMetadataMixin):
    """
    A container of Igt objects, as well as corpus-level attributes and
    metadata. In serialization formats (e.g. XigtXML), XigtCorpus
    becomes the root element.

    Args:
        id: corpus identifier
        attributes: corpus-level attributes
        metadata: corpus-level |Metadata|
        igts: iterator of |Igt|
        mode: how to instantiate the corpus (default: `full`).
            Possible values include:

            =========== ================================================
               Value        Description
            =========== ================================================
            full        Preload all |Igt| and store them in memory
                        during initialization
            incremental Load each |Igt| as needed, and keep them in
                        memory
            transient   Load each |Igt| as needed, but don't keep them
                        in memory; useful for piped input processing
            =========== ================================================
    """
    def __init__(self, id=None, attributes=None, metadata=None, igts=None,
                 mode='full'):
        XigtMixin.__init__(self)
        XigtAttributeMixin.__init__(self, id=id, attributes=attributes)
        XigtMetadataMixin.__init__(self, metadata)
        self.mode = mode
        if mode == 'full':
            self.add_list(igts)
        else:
            self._generator = igts

    def __iter__(self):
        if self.mode == 'full':
            for igt in XigtMixin.__iter__(self):
                yield igt
        else:
            for igt in self._generator:
                if self.mode == 'incremental':
                    self.add(igt)
                yield igt
            self.mode = 'full'

    @property
    def igts(self):
        return self._list

    @igts.setter
    def igts(self, value):
        self._list = value


class Igt(XigtMixin, XigtAttributeMixin, XigtMetadataMixin):
    """
    An IGT (Interlinear Glossed Text) instance.
    """
    def __init__(self, id=None, type=None, attributes=None, metadata=None,
                 tiers=None, corpus=None):
        XigtMixin.__init__(self)
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )
        XigtMetadataMixin.__init__(self, metadata)
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

    def auto_align_tiers(self,
                         tier_ids=None,
                         delimiters=item_delimiters):
        """
        Attempt to align the contents of contained tiers automatically.

        If a tier B aligns to tier A and A splits into the same number
        of tokens as items in B, align the items one-to-one.

        Args:
            tier_ids: a list of tier identifiers of the tiers to align
            delimiters:
        """
        delims = [map(re.compile, r'|'.join(eq_class))
                  for eq_class in delimiters]
        if tier_ids is None:
            tier_ids = [t.id for t in self.tiers]
        for tier_id in tier_ids:
            try:
                tier = self.get(tier_id)
                tgt_tier = tier.get_aligned_tier('alignment')
                # do something here
            except XigtError as ex:
                logging.debug('Could not align Tier {}.\n'
                              '  Reason: {}'.format(tier_id, str(ex)))
                continue

    def _auto_align_items(self, tier):
        pass


class Tier(XigtMixin, XigtAttributeMixin, XigtMetadataMixin):
    """
    A tier of IGT data. A tier should contain homogenous Items of
    data, such as all words or all glosses.
    """
    def __init__(self, id=None, type=None,
                 alignment=None, content=None, segmentation=None,
                 attributes=None, metadata=None,
                 items=None, igt=None):
        XigtMixin.__init__(self)
        XigtAttributeMixin.__init__(
            self, id=id, type=type,
            alignment=alignment, content=content, segmentation=segmentation,
            attributes=attributes
        )
        XigtMetadataMixin.__init__(self, metadata)
        self.add_list(items)
        self._parent = igt

    def __repr__(self):
        return 'Tier({}, {}, {}, {} items)'.format(
            str(self.type), str(self.id), str(self.attributes), len(self.items)
        )

    @property
    def igt(self):
        return self._parent

    @property
    def corpus(self):
        try:
            return self.igt.corpus
        except AttributeError:
            return None

    @property
    def items(self):
        return self._list

    @items.setter
    def items(self, value):
            self._list = value

    def get_aligned_tier(self, algnattr):
        tgt_tier_id = self.get_attribute(algnattr)
        if tgt_tier_id is None:
            raise XigtAttributeError(
                'Tier {} does not specify an alignment "{}".'
                .format(tgt_tier_id, algnattr)
            )
        tgt_tier = self.igt.get(tgt_tier_id)
        return tgt_tier


class Item(XigtAttributeMixin):
    """
    A single datum on a Tier. Often these are tokens, such as words
    or glosses, but may be phrases, translations, or (via extensions)
    more complex data like syntax nodes or dependencies.
    """
    def __init__(self, id=None, type=None,
                 alignment=None, content=None, segmentation=None,
                 attributes=None, text=None, tier=None):
        XigtAttributeMixin.__init__(
            self, id=id, type=type,
            alignment=alignment, content=content, segmentation=segmentation,
            attributes=attributes
        )
        self.text = text
        self._parent = tier  # mainly used for alignment expressions

    def __repr__(self):
        return 'Item({}, {}, {}, "{}")'.format(
            *map(
                str,
                [self.type, self.id, self.attributes, self.get_content()]
            )
        )

    def __str__(self):
        return str(self.get_content())

    @property
    def tier(self):
        return self._parent

    @property
    def igt(self):
        try:
            return self.tier.igt
        except AttributeError:
            return None

    @property
    def corpus(self):
        try:
            return self.igt.corpus
        except AttributeError:
            return None

    def get_content(self, resolve=True):
        if self.text is not None:
            return self.text
        elif resolve:
            if self.content is not None:
                return self.resolve_ref(CONTENT)
            elif self.segmentation is not None:
                return self.resolve_ref(SEGMENTATION)
        # all other cases
        return None

    def resolve_ref(self, refattr):
        try:
            algnexpr = self.attributes[refattr]
            reftier_id = self.tier.attributes[refattr]
            reftier = self.igt[reftier_id]
            return resolve_alignment_expression(algnexpr, reftier)
        except KeyError:
            return None  # TODO: log this

    def span(self, start, end):
        c = self.get_content()
        if c is None:
            return None
        return c[start:end]


class Metadata(object):
    """
    A container for metadata on XigtCorpus, Igt, or Tier objects.
    Extensions may place constraints on the allowable metadata.
    """
    def __init__(self, type=None, attributes=None, text=None):
        self.type = type
        self.attributes = OrderedDict(attributes or [])
        self.text = text

    def __repr__(self):
        return 'Metadata({},"{}")'.format(str(self.type), self.text)


class Meta(object):
    def __init__(self, type, attributes=None, text=None):
        self.type = type
        self.attributes = OrderedDict(attributes or [])
        self.text = text

    def __repr__(self):
        parts = [str(self.type)]
        parts.extend('{}="{}"'.format(k, v)
                     for k, v in self.attributes.items())
        if self.text is not None:
            parts.extend('"{}"'.format(self.text))
        return 'Meta({})'.format(', '.join(parts))


### Alignment Expressions ####################################################

# Module variables
algnexpr_re = re.compile(r'(([a-zA-Z][\-.\w]*)(\[[^\]]*\])?|\+|,)')
selection_re = re.compile(r'(-?\d+:-?\d+|\+|,)')

delim1 = ''
delim2 = ' '


def get_alignment_expression_ids(expression):
    alignments = algnexpr_re.findall(expression or '')
    return [item_id for _, item_id, _ in alignments if item_id]


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
        return item.get_content()
    spans = selection_re.findall(selection)
    parts = [plus if match == '+' else
             comma if match == ',' else
             item.span(*map(int, match.split(':')))
             for match in spans]
    return ''.join(parts)


# Auxiliary Functions ########################################################

def segment_tier(tier, delimiters=None, keep_delimiters=True):
    """
    Attempt to automatically segment the items in a tier. The segmented
    items are returned as a list, and the original tier is unchanged.

    Args:
        tier: A Tier object whose items will be used for segmentation.
        delimiters: A list of strings to split on. If None, default
            delimiters are used if they are defined for tier type in
            the module-level dictionary `item_delimiters`.
    Returns:
        A list of Item objects.
    """
    if delimiters is None:
        delimiters = item_delimiters.get(tier.type)

    items = []
    for item in tier:
        item.get_content()
