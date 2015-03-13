
#
# This module contains classes implementing the Xigt data model.
# Common members and methods may be found in the xigt.mixins module,
# so take note of the class inheritance below.
#

import logging
import warnings
from collections import OrderedDict
from itertools import chain

from xigt.mixins import (
    XigtContainerMixin,  # XigtCorpus, Igt, Tier, Metadata
    XigtAttributeMixin,  # XigtCorpus, Igt, Tier, Item, Metadata, Meta
    XigtReferenceAttributeMixin,  # Tier, Item
    XigtMetadataMixin  # XigtCorpus, Igt, Tier
)

from xigt.errors import (
    XigtError,
    XigtStructureError,
    XigtAttributeError,
    XigtWarning
)


class XigtCorpus(XigtContainerMixin, XigtAttributeMixin, XigtMetadataMixin):
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
            incremental Load each |Igt| sequentially as needed, and keep
                        them in memory
            transient   Load each |Igt| sequentially as needed, but
                        don't keep them in memory; useful for piped
                        input processing
            =========== ================================================
    """
    def __init__(self, id=None, attributes=None, metadata=None, igts=None,
                 mode='full'):
        XigtContainerMixin.__init__(self)
        XigtAttributeMixin.__init__(self, id=id, attributes=attributes)
        XigtMetadataMixin.__init__(self, metadata)
        self.mode = mode
        if mode == 'full':
            self.extend(igts or [])
        else:
            self._generator = igts

    def __repr__(self):
        return '<XigtCorpus object (id: {}) with {} Igts at {}>'.format(
            str(self.id or '--'), len(self), str(id(self))
        )

    def __iter__(self):
        if self.mode == 'full':
            for igt in XigtContainerMixin.__iter__(self):
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


class Igt(XigtContainerMixin, XigtAttributeMixin, XigtMetadataMixin):
    """
    An IGT (Interlinear Glossed Text) instance.
    """
    def __init__(self, id=None, type=None, attributes=None, metadata=None,
                 tiers=None, corpus=None):
        XigtContainerMixin.__init__(self)
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )
        XigtMetadataMixin.__init__(self, metadata)
        self.extend(tiers or [])
        self._parent = corpus

    def __repr__(self):
        return '<Igt object (id: {}) with {} Tiers at {}>'.format(
            str(self.id or '--'), len(self), str(id(self))
        )

    @property
    def corpus(self):
        return self._parent

    @property
    def tiers(self):
        return self._list
    @tiers.setter
    def tiers(self, value):
        self._list = value


class Tier(XigtContainerMixin, XigtAttributeMixin,
           XigtReferenceAttributeMixin, XigtMetadataMixin):
    """
    A tier of IGT data. A tier should contain homogenous Items of
    data, such as all words or all glosses.
    """
    def __init__(self, id=None, type=None,
                 alignment=None, content=None, segmentation=None,
                 attributes=None, metadata=None,
                 items=None, igt=None):
        XigtContainerMixin.__init__(self)
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )
        XigtMetadataMixin.__init__(self, metadata)
        self.alignment = alignment
        self.content = content
        self.segmentation = segmentation

        self.extend(items or [])
        self._parent = igt

    def __repr__(self):
        return '<Tier object (id: {}; type: {}) with {} Items at {}>'.format(
            str(self.id or '--'), self.type, len(self), str(id(self))
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


class Item(XigtAttributeMixin, XigtReferenceAttributeMixin):
    """
    A single datum on a Tier. Often these are tokens, such as words
    or glosses, but may be phrases, translations, or (via extensions)
    more complex data like syntax nodes or dependencies.
    """
    def __init__(self, id=None, type=None,
                 alignment=None, content=None, segmentation=None,
                 attributes=None, text=None, tier=None):
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )
        self.alignment = alignment
        self.content = content
        self.segmentation = segmentation

        self.text = text
        self._parent = tier  # mainly used for alignment expressions

    def __repr__(self):
        return '<Item object (id: {}) with value "{}" at {}>'.format(
            str(self.id or '--'), self.value(), str(id(self))
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

    def value(self, resolve=True):
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

    # deprecated methods

    def get_content(self, resolve=True):
        warnings.warn(
            'Item.get_content() is deprecated; use Item.value() instead.',
            DeprecationWarning
        )
        return self.value(resolve=resolve)

    def span(self, start, end):
        warnings.warn(
            'Item.span(i1, i2) is deprecated; '
            'use Item.value()[i1:i2] instead.',
            DeprecationWarning
        )

        c = self.value()
        if c is None:
            return None
        return c[start:end]


def metadata_text_warning():
    warnings.warn(
        'Metadata.text is deprecated; use Metadata.metas instead.',
        DeprecationWarning
    )

class Metadata(XigtContainerMixin, XigtAttributeMixin):
    """
    A container for metadata on XigtCorpus, Igt, or Tier objects.
    Extensions may place constraints on the allowable metadata.
    """
    def __init__(self, id=None, type=None, attributes=None,
                 text=None, metas=None):
        XigtContainerMixin.__init__(self)
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )

        if text is not None:
            metadata_text_warning()
            if metas is not None:
                raise XigtError(
                    'text and metas cannot both be specified.'
                )
            if isinstance(text, str):
                warnings.warn(
                    'String values of Metadata are deprecated; '
                    'it will be put in an untyped Meta object.',
                    DeprecationWarning
                )
                text = [Meta(text=text)]
            metas = text

        self.extend(metas or [])

    def __repr__(self):
        return '<Metadata object (id: {}) with {} Metas at {}>'.format(
            str(self.id or '--'), len(self), str(id(self))
        )

    @property
    def metas(self):
        return self._list
    @metas.setter
    def metas(self, value):
            self._list = value

    # deprecated properties

    @property
    def text(self):
        metadata_text_warning()
        return self.metas
    @text.setter
    def text(self, value):
        metadata_text_warning()
        self.metas = value


class Meta(XigtAttributeMixin):
    def __init__(self, id=None, type=None, attributes=None, text=None):
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )

        self.text = text

    def __repr__(self):
        return '<Meta object (id: {}) at {}>'.format(
            str(self.id or '--'), str(id(self))
        )
