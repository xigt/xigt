
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

# list.clear() doesn't exist in Python2, but del list[:] has other problems
try:
    [].clear
except AttributeError:
    def listclear(x): del x[:]
else:
    def listclear(x): list.clear(x)

def _has_parent(obj):
    return hasattr(obj, '_parent') and obj._parent is not None


class XigtContainerMixin(list):
    """
    Common methods for accessing subelements in XigtCorpus, Igt, and
    Tier objects.
    """
    def __init__(self, container=None, contained_type=None):
        self._dict = {}
        self._contained_type = contained_type
        self._container = container if container is not None else self

    def __eq__(self, other):
        try:
            return (
                # quick check for comparing, e.g., XigtCorpus and Igt
                self._contained_type == other._contained_type
                and len(self) == len(other)
                and all(a == b for a, b in zip(self, other))
            )
        except AttributeError:
            return False

    def __getitem__(self, obj_id):
        if isinstance(obj_id, (int, slice)):
            return list.__getitem__(self, obj_id)
        elif obj_id in self._dict:
            return self._dict[obj_id]
        else:
            try:
                return list.__getitem__(self, int(obj_id))
            except ValueError:
                pass
        raise KeyError(obj_id)

    def __setitem__(self, idx, obj):
        # only allow list indices, not dict keys (IDs)
        # NOTE: this method is destructive. check for broken refs here?
        self._assert_type(obj)
        try:
            cur_obj = list.__getitem__(self, idx)
        except TypeError:
            idx = int(idx)
            cur_obj = list.__getitem__(self, idx)
        if cur_obj.id is not None:
            del self._dict[cur_obj.id]
        self._create_id_mapping(obj)
        list.__setitem__(self, idx, obj)

    def __delitem__(self, obj_id):
        # NOTE: this method is destructive. check for broken refs here?
        obj = self[obj_id]
        self.remove(obj)

    def get(self, obj_id, default=None):
        try:
            return self[obj_id]
        except (KeyError, IndexError):
            pass
        return default

    def select(self, **kwargs):
        # handle namespace separately so we can lookup the nsmap
        if 'namespace' in kwargs and kwargs['namespace'] in self.nsmap:
            kwargs['namespace'] = self.nsmap[kwargs['namespace']]
        def match(x):
            return all(getattr(x, k, None) == v for k, v in kwargs.items())
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
        list.append(self, obj)

    def insert(self, i, obj):
        self._assert_type(obj)
        obj._parent = self._container
        self._create_id_mapping(obj)
        list.insert(self, i, obj)

    def extend(self, objs):
        for obj in objs:
            self.append(obj)

    def remove(self, obj):
        # NOTE: this method is destructive. check for broken refs here?
        if obj.id is not None:
            del self._dict[obj.id]
        list.remove(self, obj)

    def clear(self):
        self._dict.clear()
        # list.clear doesn't exist in Python2
        # list.clear(self)
        listclear(self)

    def _create_id_mapping(self, obj):
        if obj.id is not None:
            if obj.id in self._dict:
                raise XigtError(
                    'Id "{}" already exists in collection.'.format(obj.id),
                )
            self._dict[obj.id] = obj

    def refresh_index(self):
        self._dict = {}
        for obj in self:
            self._create_id_mapping(obj)

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
        self.nsmap = nsmap
        # if id is not None or ID not in self.attributes:
        #     self.attributes[ID] = id
        # if type is not None or TYPE not in self.attributes:
        #     self.attributes[TYPE] = type

    def __eq__(self, other):
        try:
            return (
                self.id == other.id
                and self.type == other.type
                and self.attributes == other.attributes
                and self.namespace == other.namespace
                # and self.nsmap == other.nsmap
            )
        except AttributeError:
            return False

    def get_attribute(self, key, default=None, inherit=False, namespace=None):
        if key is None:
            raise ValueError(
                'Attribute key must be of type str, not '
                + key.__class__.__name__
            )
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

    @property
    def nsmap(self):
        if self._nsmap is None:
            if _has_parent(self):
                return self._parent.nsmap
            else:
                return {}
        else:
            return self._nsmap
    @nsmap.setter
    def nsmap(self, value):
        if value is not None:
            value = dict(value or [])
        self._nsmap = value


    # no validation for type yet, so the property isn't necessary
    # @property
    # def type(self):
    #     return self._type
    # @type.setter
    # def type(self, value):
    #     self._type = value


class XigtReferenceAttributeMixin(object):
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
