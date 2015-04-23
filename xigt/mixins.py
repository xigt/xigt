
import warnings

from xigt.consts import (
    ID,
    TYPE,
    ALIGNMENT,
    CONTENT,
    SEGMENTATION
)
from xigt.errors import (
    XigtError,
    XigtStructureError
)
from xigt.ref import id_re

def _has_parent(obj):
    return hasattr(obj, '_parent') and obj._parent is not None


class XigtContainerMixin(object):
    """
    Common methods for accessing subelements in XigtCorpus, Igt, and
    Tier objects.
    """
    def __init__(self, container=None, contained_type=None):
        self._list = []
        self._dict = {}
        self._contained_type = contained_type
        self._container = container if container is not None else self

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
        except (KeyError, IndexError):
            pass
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

    def _assert_type(self, obj):
        if self._contained_type and not isinstance(obj, self._contained_type):
            raise XigtStructureError(
                'Only {} objects are allowed in this container.'
                .format(self._contained_type.__name__)
            )

    def append(self, obj):
        self._assert_type(obj)
        obj._parent = self._container
        self._create_id_mapping(obj)
        self._list.append(obj)

    def insert(self, i, obj):
        self._assert_type(obj)
        obj._parent = self._container
        self._create_id_mapping(obj)
        self._list.insert(i, obj)

    def extend(self, objs):
        for obj in objs:
            self.append(obj)

    def _create_id_mapping(self, obj):
        if obj.id is not None:
            if obj.id in self._dict:
                raise XigtError(
                    'Id "{}" already exists in collection.'.format(obj.id),
                )
            self._dict[obj.id] = obj

    def refresh_index(self):
        self._dict = {}
        for obj in self._list:
            self._create_id_mapping(obj)

    def clear(self):
        self._dict = {}
        self._list = []

    # deprecated methods

    def add(self, obj):
        warnings.warn(
            'add(x) is deprecated; use append(x) instead.',
            DeprecationWarning
        )
        return self.append(obj)

    def add_list(self, objs):
        warnings.warn(
            'add_list(xs) is deprecated; use extend(xs) instead.',
            DeprecationWarning
        )
        return self.extend(objs)


class XigtAttributeMixin(object):

    def __init__(self, id=None, type=None, attributes=None,
                 namespace=None, nsmap=None):
        self.id = id
        self.type = type
        self.attributes = dict(attributes or [])
        self.namespace = namespace
        self.nsmap = dict(nsmap or [])
        # if id is not None or ID not in self.attributes:
        #     self.attributes[ID] = id
        # if type is not None or TYPE not in self.attributes:
        #     self.attributes[TYPE] = type

    def get_attribute(self, key, default=None, inherit=False, namespace=None):
        if not key.startswith('{') and ':' in key:
            prefix, suffix = key.split(':', 1)
            key = '{%s}%s' % (self.nsmap[prefix], suffix)
        elif namespace in self.nsmap:
            key = '{%s}%s' % (self.nsmap[namespace], key)
        elif namespace:
            key = '{%s}%s' % (namespace, key)
        try:
            return self.attributes[key]
        except KeyError:
            if inherit and _has_parent(self):
                return self._parent.get_attribute(
                    key, default, inherit, namespace=namespace
                )
            else:
                return default

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        if value is not None and not id_re.match(value):
            raise ValueError('Invalid ID: {}'.format(value))
        self._id = value

    # no validation for type yet, so the property isn't necessary
    # @property
    # def type(self):
    #     return self._type
    # @type.setter
    # def type(self, value):
    #     self._type = value


class XigtReferenceAttributeMixin(object):

    _tier_refattrs = {
        None: (ALIGNMENT, CONTENT, SEGMENTATION)
    }
    _item_refattrs = {
        None: {
            None: (ALIGNMENT, CONTENT, SEGMENTATION)
        }
    }

    def __init__(self, alignment=None, content=None, segmentation=None):

        if segmentation and (content or alignment):
            raise XigtError(
                'The "segmentation" reference attribute cannot co-occur with '
                'the "content" or "alignment" reference attributes.'
            )

        if alignment is not None:
            self.attributes[ALIGNMENT] = alignment
        if content is not None:
            self.attributes[CONTENT] = content
        if segmentation is not None:
            self.attributes[SEGMENTATION] = segmentation

    def referents(self, refattrs=None):
        if not getattr(self, 'igt'):
            raise XigtError('Cannot retrieve referents; unspecified IGT.')
        if not getattr(self, 'id'):
            raise XigtError('Cannot retrieve referents; unspecified id.')
        return self.igt.referents(self.id, refattrs=refattrs)

    def referrers(self, refattrs=None):
        if not getattr(self, 'igt'):
            raise XigtError('Cannot retrieve referrers; unspecified IGT.')
        if not getattr(self, 'id'):
            raise XigtError('Cannot retrieve referrers; unspecified id.')
        return self.igt.referrers(self.id, refattrs=refattrs)

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

    def allowed_reference_attributes(self):
        # tiers just get _tier_refattrs[tier.type], items get
        # _item_refattrs[tier.type][item.type]. If a type is not
        # specified, it defaults to None.
        try:
            tier_type = self.tier.type
        except AttributeError:
            return self._tier_refattrs.get(self.type, self._tier_refattrs[None])
        else:
            ras = self._item_refattrs.get(tier_type, self._item_refattrs[None])
            return ras.get(self.type, ras[None])

