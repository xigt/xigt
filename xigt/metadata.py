
import warnings

from xigt.mixins import (
    XigtContainerMixin,
    XigtAttributeMixin
)
from xigt.errors import XigtError


class XigtMetadataMixin(object):
    """
    Enables the management of metadata.
    """
    def __init__(self, metadata=None):
        self._md = XigtContainerMixin(container=self, contained_type=Metadata)
        if metadata is not None:
            self.metadata = metadata

    @property
    def metadata(self):
        return self._md
    @metadata.setter
    def metadata(self, value):
        if isinstance(value, Metadata):
            raise XigtError('The metadata attribute must be a sequence '
                            'of Metadata objects.')
        self._md.clear()
        self._md.extend(value)

    # possibly pending deprecation

    def get_meta(self, key, conditions=None, default=None, inherit=True):
        if conditions is None:
            conditions = []
        metas = []
        for metadata in self.metadata:
            if metadata.type != 'xigt-meta':
                continue
            for meta in metadata.metas:
                if meta.type == key and all(c(meta) for c in conditions):
                    metas.append(meta)
        if metas:
            return metas
        elif inherit and hasattr(self, '_parent') and self._parent is not None:
            return self._parent.get_meta(key, conditions, default, inherit)
        else:
            return default


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
        XigtContainerMixin.__init__(self, contained_type=Meta)
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
    def __init__(self, id=None, type=None, attributes=None, text=None,
                 children=None, metadata=None):
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes
        )

        self._parent = metadata
        self.text = text
        self.children = children

    def __repr__(self):
        return '<Meta object (id: {}) at {}>'.format(
            str(self.id or '--'), str(id(self))
        )
