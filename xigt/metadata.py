
import warnings
import re

from xigt.mixins import (
    XigtContainerMixin,
    XigtAttributeMixin
)
from xigt.errors import XigtError

# name_re approximately follows the XML 1.0 spec for Name productions,
# so long as the re character classes correspond to XML productions.
# This also excludes colons in the name (because of potential trouble
# with xml processors treating them as namespace delimiters)
# http://www.w3.org/TR/2000/WD-xml-2e-20000814#NT-Name
name_re = re.compile(r'^[^\W\d][-.\w]*$')

class XigtMetadataMixin(object):
    """
    Enables the management of metadata.
    """
    def __init__(self, metadata=None):
        self._md = XigtContainerMixin(container=self, contained_type=Metadata)
        if metadata is not None:
            self.metadata = metadata

    def __eq__(self, other):
        try:
            return self._md == other._md
        except AttributeError:
            return False

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
                 text=None, metas=None, namespace=None, nsmap=None):
        XigtContainerMixin.__init__(self, contained_type=Meta)
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes,
            namespace=namespace, nsmap=nsmap
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

    def __eq__(self, other):
        return (
            XigtContainerMixin.__eq__(self, other)
            and XigtAttributeMixin.__eq__(self, other)
        )

    @property
    def metas(self):
        return list(self)
    @metas.setter
    def metas(self, value):
        self.clear()
        self.extend(value or [])

    # deprecated properties

    @property
    def text(self):
        metadata_text_warning()
        return self.metas
    @text.setter
    def text(self, value):
        metadata_text_warning()
        self.metas = value


class Meta(XigtContainerMixin, XigtAttributeMixin):
    def __init__(self, id=None, type=None, attributes=None, text=None,
                 children=None, metadata=None, namespace=None, nsmap=None):
        XigtContainerMixin.__init__(self, contained_type=MetaChild)
        XigtAttributeMixin.__init__(
            self, id=id, type=type, attributes=attributes,
            namespace=namespace, nsmap=nsmap
        )

        self._parent = metadata
        self.text = text
        self.extend(children or [])

    def __repr__(self):
        return '<Meta object (id: {}) at {}>'.format(
            str(self.id or '--'), str(id(self))
        )

    def __eq__(self, other):
        try:
            return (
                self.text == other.text
                and XigtContainerMixin.__eq__(self, other)
                and XigtAttributeMixin.__eq__(self, other)
            )
        except AttributeError:
            return False

    @property
    def children(self):
        return list(self)
    @children.setter
    def children(self, value):
        self.clear()
        self.extend(value or [])


class MetaChild(XigtContainerMixin, XigtAttributeMixin):
    def __init__(self, name, attributes=None, text=None,
                 children=None, parent=None, namespace=None, nsmap=None):
        XigtContainerMixin.__init__(self, contained_type=MetaChild)
        XigtAttributeMixin.__init__(
            self, id=None, type=None, attributes=attributes,
            namespace=namespace, nsmap=nsmap
        )

        if not name_re.match(name):
            raise ValueError('Invalid name for MetaChild: {}'.format(name))
        self.name = name
        self._parent = parent
        self.text = text
        self.extend(children or [])

    def __repr__(self):
        return '<MetaChild object (name: {}) at {}>'.format(
            str(self.name or '--'), str(id(self))
        )

    def __eq__(self, other):
        try:
            return (
                self.name == other.name
                and self.text == other.text
                and XigtContainerMixin.__eq__(self, other)
                and XigtAttributeMixin.__eq__(self, other)
            )
        except AttributeError:
            return False

    @property
    def children(self):
        return list(self)
    @children.setter
    def children(self, value):
        self.clear()
        self.extend(value or [])
