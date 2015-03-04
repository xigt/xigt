import re
import logging
import warnings
from collections import OrderedDict
from itertools import chain

from xigt.errors import (
    XigtError,
    XigtStructureError,
    XigtAttributeError,
    XigtWarning
)

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


def metadata_text_warning():
    warnings.warn(
        'Metadata.text is deprecated; use Metadata.metas instead.',
        DeprecationWarning
    )

class Metadata(object):
    """
    A container for metadata on XigtCorpus, Igt, or Tier objects.
    Extensions may place constraints on the allowable metadata.
    """
    def __init__(self, type=None, attributes=None, text=None, metas=None):
        self.type = type
        self.attributes = OrderedDict(attributes or [])
        if text is not None:
            metadata_text_warning()
            if metas is not None:
                raise XigtError(
                    'text and metas cannot both be specified.'
                )
            metas = text
        self.metas = metas or []

    def __repr__(self):
        return 'Metadata({},"{}")'.format(str(self.type), self.text)

    # the text property should be removed in some later version
    @property
    def text(self):
        metadata_text_warning()
        return self.metas

    @text.setter
    def text(self, value):
        metadata_text_warning()
        self.metas = value


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
